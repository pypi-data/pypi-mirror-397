# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Target encoder."""

import collections
import logging
import warnings

import torch
from nemotron_ocr.inference.post_processing.data.text_region import Batch, TextRegion
from nemotron_ocr.inference.post_processing.data.worker_messages import TargetEncoderMessage

from nemotron_ocr.inference.models.utils import is_named_tuple

_PREPARED_KEY = "_prepared_base"

logger = logging.getLogger(__name__)


@torch.jit.script
def are_verts_outside(
    vertices: torch.Tensor, x_max: float, y_max: float, x_min: float = 0, y_min: float = 0
):
    x = vertices[:, 0]
    y = vertices[:, 1]
    are_outside = torch.logical_or(
        torch.logical_or(x < x_min, x > x_max), torch.logical_or(y < y_min, y > y_max)
    )

    return are_outside


class TargetEncoderBase(object):
    """Class that handles encoding of targets and sending them to the gpu."""

    def __init__(self, input_size, amp_opt, verbose=False):
        """Initializes the target encoder."""
        self.input_size = input_size
        self.amp_opt = amp_opt
        self.verbose = verbose

    def prepare_data(self, batch: Batch, input_sizes):
        """Operates on object_batch in a mutable manner."""
        if getattr(batch, _PREPARED_KEY, None) is not None:
            return

        for example, input_size in zip(batch, input_sizes):
            im_width = input_size[-1]
            im_height = input_size[-2]

            coal = example.coalesce_homogeneous()
            are_outside = are_verts_outside(coal, im_width, im_height)

            offset = 0
            for r_i in range(len(example)):
                region = example[r_i]
                num_vertices = region.region.vertices.shape[0]
                if not region.valid:
                    offset += num_vertices
                    continue

                tr_outside = are_outside[offset : offset + num_vertices]
                offset += num_vertices

                any_outside = torch.any(tr_outside).item()

                # If it straddles the boundary, then mark it as invalid so that the
                # net doesn't get penalized either way
                if any_outside:
                    region.valid = False

        setattr(batch, _PREPARED_KEY, True)

    def _convert_labels_to_targets(self, object_batch, input_sizes):
        """Place holder for labels to target conversion."""
        raise NotImplementedError("Subclasses must implement this function!")

    def convert_labels_to_targets(self, object_batch, input_sizes):
        self.prepare_data(object_batch, input_sizes)

        return self._convert_labels_to_targets(object_batch, input_sizes)

    def send_targets_to_gpu(self, targets, **kwargs):
        """Sends targets to the gpu."""
        if torch.is_tensor(targets):
            if targets.numel() > 0:
                r = targets.cuda(**kwargs)
            else:
                r = torch.empty(*targets.shape, dtype=targets.dtype, device="cuda")
            return r

        if isinstance(targets, str):
            return targets

        # Look for a dict type object
        if isinstance(targets, collections.abc.Mapping):
            return {
                k: self.send_targets_to_gpu(v, **kwargs)
                for k, v in targets.items()
                if k != "__other"
            }

        # Look for a namedtuple
        if is_named_tuple(targets):
            return type(targets)(*[self.send_targets_to_gpu(t, **kwargs) for t in targets])

        if isinstance(targets, collections.abc.Iterable):
            return type(targets)([self.send_targets_to_gpu(t, **kwargs) for t in targets])

        # Nothing that can be sent to the GPU, so just return it back
        return targets

    def convert_targets_to_labels(
        self, target_dict, image_size, limit_idxs=None, is_gt=True, **kwargs
    ) -> Batch:
        raise NotImplementedError("Subclasses must implement this function!")

    def is_recognition(self):
        return False

    def get_charset(self):
        raise ValueError("This target encoder does not support charsets!")

    def handle_message(self, message: TargetEncoderMessage):
        warnings.warn(f"No known message can handle type {type(message)}!")

    def send_messages(self, worker_comm_context, gpu_targets, **kwargs):
        pass

    def get_state_dict(self):
        state_dict = dict()
        self.build_state_dict(state_dict)
        return state_dict

    def build_state_dict(self, state_dict):
        pass

    def load_state_dict(self, state_dict):
        pass

    def get_rrect_and_quad(self, region: TextRegion):
        verts = region.region.vertices
        if verts.shape[0] < 4:
            verts = torch.cat([verts, verts[:1].expand(4 - verts.shape[0], 2)])
        try:
            rrect = region.region.min_rrect
        except:  # noqa: E722
            rrect = region.region.bounds_quad
            region.valid = False
        vtx_count = verts.shape[0]

        quad = verts if vtx_count == 4 else rrect

        return rrect, quad
