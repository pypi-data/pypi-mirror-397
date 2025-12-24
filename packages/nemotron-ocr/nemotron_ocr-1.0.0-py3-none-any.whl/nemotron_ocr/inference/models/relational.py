# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import math

import torch
import torch.nn as nn

from nemotron_ocr.inference.models import blocks
from nemotron_ocr.inference.models.utils import options

from nemotron_ocr_cpp import (
    quad_rectify_calc_quad_width,
    ragged_quad_all_2_all_distance_v2,
)


logger = logging.getLogger(__name__)


NULL_CONNECTION_WEIGHT = -math.inf


class GlobalRelationalModel(nn.Module):
    def __init__(self, num_input_channels, recog_feature_depth, k=32, dropout=0.1, num_layers=4):
        super().__init__()

        num_input_channels = num_input_channels[-1]
        self.pos_channels = 14  # 64
        self.current_step = 0
        self.total_steps = 1
        self.k = k
        self.quad_rectify_grid_size = (2, 3)
        self.quad_downscale = 1024.0
        self.inference_mode = False

        self.grid_size = [2, 3]
        self.isotropic = False

        self.initial_depth = 128

        self.rect_proj = blocks.conv2d_block(num_input_channels, num_input_channels, 1)

        self.recog_tx = nn.Linear(recog_feature_depth, num_input_channels)

        # Reserve 2 channels for the joint distance and angle embeddings
        initial_depth = self.initial_depth - 1 - self.pos_channels
        cb_input = 2 * num_input_channels  # + self.pos_channels
        self.combined_proj = nn.Sequential(
            nn.Linear(cb_input, cb_input),
            nn.BatchNorm1d(cb_input),
            nn.ReLU(),
            nn.Linear(cb_input, initial_depth),
            nn.BatchNorm1d(initial_depth),
            nn.ReLU(),
        )

        dim = 2 * self.initial_depth

        self.encoder = nn.Sequential(
            nn.TransformerEncoder(
                nn.TransformerEncoderLayer(
                    dim, 8, 2 * dim, batch_first=True, dropout=dropout, norm_first=True
                ),
                num_layers=num_layers,
            ),
            nn.Linear(dim, 3),
        )

    def get_target_rects(
        self,
        quads: torch.Tensor,
        curr_rects: torch.Tensor,
        curr_centers: torch.Tensor,
        gt_relations: torch.Tensor,
    ):
        to_rects = curr_rects.unsqueeze(0).expand(curr_rects.shape[0], -1, -1)
        to_centers = curr_centers.unsqueeze(0).expand(quads.shape[0], -1, -1)

        k = max(0, min(to_rects.shape[1] - 1, self.k - 1))

        if k == 0:
            to_rects = torch.zeros(
                curr_rects.shape[0], 1, curr_rects.shape[1] + 2, **options(curr_rects)
            )
            closest_other_idxs = torch.zeros(
                curr_rects.shape[0], 1, dtype=torch.int64, device=curr_rects.device
            )
        else:
            all_dists = get_cdist(quads, curr_centers)

            closest_other_idxs = torch.topk(
                all_dists, k=k, dim=1, largest=False, sorted=False
            ).indices

            # K,K-1,D
            to_rects = torch.gather(
                to_rects,
                dim=1,
                index=closest_other_idxs.unsqueeze(2).expand(-1, -1, curr_rects.shape[1]),
            )
            # K,K-1
            all_dists = torch.gather(all_dists, dim=1, index=closest_other_idxs)
            # K,K-1,2
            to_centers = torch.gather(
                to_centers, dim=1, index=closest_other_idxs.unsqueeze(2).expand(-1, -1, 2)
            )

            # Add the null column to rects
            to_rects = torch.cat(
                (
                    torch.zeros(to_rects.shape[0], 1, to_rects.shape[2], **options(to_rects)),
                    to_rects,
                ),
                dim=1,
            )

            # Add the null column to the dists
            all_dists = torch.cat(
                (
                    torch.full((all_dists.shape[0], 1), -1, **options(all_dists)),
                    all_dists,
                ),
                dim=1,
            )

            directions = get_directions(quads, to_centers)
            directions = torch.cat(
                (
                    torch.full((directions.shape[0], 1), -2, **options(directions)),
                    directions,
                ),
                dim=1,
            )

            # Add the pairwise geometric encodings
            to_rects = torch.cat(
                (
                    to_rects,
                    all_dists.unsqueeze(2),
                    directions.unsqueeze(2),
                ),
                dim=2,
            )

            # Add the null column
            closest_other_idxs = torch.cat(
                [
                    torch.zeros(closest_other_idxs.shape[0], 1, **options(closest_other_idxs)),
                    closest_other_idxs + 1,
                ],
                dim=1,
            )

        return to_rects, closest_other_idxs

    def prohibit_self_connection(self, dots: torch.Tensor, closest_other_idxs: torch.Tensor = None):
        dots = dots.float()

        if closest_other_idxs is None:
            neg_inf = torch.full((dots.shape[-2],), NULL_CONNECTION_WEIGHT, **options(dots)).diag()

            neg_inf = torch.cat(
                (torch.zeros(neg_inf.shape[0], 1, **options(neg_inf)), neg_inf), dim=1
            )

            if dots.ndim == 3:
                neg_inf.unsqueeze_(0)

            dots = dots + neg_inf
        else:
            neg_inf = torch.full(
                (*dots.shape[:-2], dots.shape[-2], dots.shape[-2] + 1),
                NULL_CONNECTION_WEIGHT,
                **options(dots),
            )

            if dots.ndim == 3:
                closest_other_idxs = closest_other_idxs.unsqueeze(0).expand_as(dots)

            neg_inf = torch.scatter(neg_inf, dim=-1, index=closest_other_idxs, src=dots)
            dots = neg_inf

        return dots

    def get_input_encoding(
        self,
        rectified_quads: torch.Tensor,
        original_quads: torch.Tensor,
        region_counts: torch.Tensor,
        recog_features: torch.Tensor,
    ):
        cs_rg = torch.cumsum(region_counts, 0)
        cs_rg = torch.cat([torch.tensor([0]), cs_rg])
        ex_offsets = cs_rg

        g_height, g_width = self.quad_rectify_grid_size
        if self.isotropic:
            # Figure out the number of valid positions for each quad, which we can use to compute the mean
            quad_widths = quad_rectify_calc_quad_width(
                original_quads, rectified_quads.shape[-2], 1, rectified_quads.shape[-1]
            )
        else:
            quad_widths = torch.full((original_quads.shape[0],), g_width, **options(original_quads))
        num_valid_pos = (quad_widths * g_height).clamp_min(1)

        # Ensure that these values aren't very large
        original_quads = original_quads / self.quad_downscale
        mid_pts = original_quads.detach().mean(dim=1, dtype=torch.float32)

        rectified_quads = self.rect_proj(rectified_quads)
        avg_rects = rectified_quads.flatten(2).sum(
            dim=2, dtype=torch.float32
        ) / num_valid_pos.unsqueeze(1)

        recog_encoding = self.recog_tx(recog_features.detach()).mean(dim=1, dtype=torch.float32)

        semantic_encoding = self.combined_proj(torch.cat((avg_rects, recog_encoding), dim=1))

        h1 = original_quads[:, 3] - original_quads[:, 0]
        h2 = original_quads[:, 2] - original_quads[:, 1]

        mp1 = original_quads[:, 0] + (h1 / 2)
        mp2 = original_quads[:, 1] + (h2 / 2)

        d1 = mp2 - mp1

        wdth = d1.norm(dim=1, keepdim=True)

        d1 = d1 / wdth.clamp_min(1e-6)

        hts = ((h1 + h2) / 2).norm(dim=1, keepdim=True)

        d2 = torch.stack([-d1[:, 1], d1[:, 0]], dim=-1)

        # Prevent overfitting to specific quad positions by translating all positions
        # by some random offset (thus preserving inter-quad relationships, but not absolute positions)
        if self.training:
            rand_quad_offset = torch.rand(1, 1, 2, **options(original_quads)) * 4 - 2

            quads_enc = original_quads + rand_quad_offset
        else:
            quads_enc = original_quads

        # The last 5 tensors represent the geometric encoding for each word

        full_encoding = torch.cat(
            (semantic_encoding, quads_enc.flatten(1), d1, d2, wdth, hts), dim=1
        )

        return full_encoding, ex_offsets, region_counts, mid_pts

    def forward(
        self,
        rectified_quads: torch.Tensor,
        original_quads: torch.Tensor,
        region_counts: torch.Tensor,
        recog_features: torch.Tensor,
    ):
        rectified_quads = rectified_quads.float()
        recog_features = recog_features.float()

        assert torch.all(torch.isfinite(rectified_quads))
        assert torch.all(torch.isfinite(recog_features))

        proj_rects, ex_offsets, region_counts, mid_pts = self.get_input_encoding(
            rectified_quads, original_quads, region_counts, recog_features
        )

        quads = original_quads / self.quad_downscale

        all_dots = dict(words=[], lines=[], line_log_var_unc=[])

        if not self.inference_mode:
            assert torch.all(torch.isfinite(proj_rects)), "Not all proj_rects were finite!"

        for i, (offset, region_count) in enumerate(zip(ex_offsets, region_counts)):
            # K,D
            curr_rects = proj_rects[offset : offset + region_count]
            curr_centers = mid_pts[offset : offset + region_count]
            curr_quads = quads[offset : offset + region_count]

            from_rects = curr_rects

            to_rects, closest_other_idxs = self.get_target_rects(
                curr_quads, curr_rects, curr_centers, None
            )

            # K,Z,D
            from_rects = from_rects.unsqueeze(1).expand(-1, to_rects.shape[1], -1)

            # K,Z+1,D*2
            enc_input = torch.cat((from_rects, to_rects), dim=2)

            # K,Z+1,2
            if enc_input.shape[0]:
                dots = self.encoder(enc_input)
            else:
                dots = torch.empty(0, 1, 3, dtype=enc_input.dtype, device=enc_input.device)

            # 2,K,Z+1
            dots = dots.permute(2, 0, 1)

            dots = self.prohibit_self_connection(dots, closest_other_idxs)

            word_pred = dots[0]
            line_pred = dots[1]
            line_log_var_pred = dots[2]

            all_dots["words"].append(word_pred)
            all_dots["lines"].append(line_pred)
            all_dots["line_log_var_unc"].append(line_log_var_pred)

        return {
            "words": all_dots["words"],
            "lines": all_dots["lines"],
            "line_log_var_unc": all_dots["line_log_var_unc"],
        }


def get_cdist(
    quads: torch.Tensor, centers: torch.Tensor, x_factor: float = 1.0, y_factor: float = 1.0
):
    region_counts = torch.tensor([quads.shape[0]], dtype=torch.int64, device=quads.device)

    ret = ragged_quad_all_2_all_distance_v2(
        quads.unsqueeze(0), region_counts, x_factor, y_factor, allow_self_distance=False
    )[0]

    return ret


def get_directions(quads: torch.Tensor, to_centers: torch.Tensor):
    quads = quads.detach()
    to_centers = to_centers.detach()

    # quads: N,4,2
    # to_centers: N,K,2

    pt0 = (quads[:, 0] + quads[:, 3]) / 2
    pt1 = (quads[:, 1] + quads[:, 2]) / 2

    direction = pt1 - pt0
    direction /= direction.norm(p=2, dim=1, keepdim=True).clamp_min(1e-6)
    direction = direction.unsqueeze(1).expand(-1, to_centers.shape[1], -1)

    centers = (pt0 + pt1) / 2

    vec_other = to_centers - centers.unsqueeze(1)
    dir_other = vec_other / vec_other.norm(p=2, dim=2, keepdim=True).clamp_min(1e-6)

    cos_angle = torch.einsum("ftv,ftv->ft", direction, dir_other)

    return cos_angle
