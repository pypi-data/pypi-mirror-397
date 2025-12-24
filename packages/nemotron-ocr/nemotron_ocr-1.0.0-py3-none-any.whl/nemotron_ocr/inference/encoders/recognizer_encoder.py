#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


"""Base target encoder for e2e recognition models."""

from collections import defaultdict, deque
import logging
import math
import os
from typing import Tuple, List, Optional, Callable, Dict

import numpy as np
import torch

import nemotron_ocr.inference.post_processing.data.text_region as tr
from nemotron_ocr.inference.post_processing.data.quadrangle import Quadrangle
from nemotron_ocr.inference.post_processing.data.worker_messages import TargetEncoderMessage
from nemotron_ocr.inference.encoders.base import TargetEncoderBase

from nemotron_ocr_cpp import (
    beam_decode,
    sparse_select,
    create_sbo_lm,
    decode_sequences,
    create_token_mapping,
)
from nemotron_ocr.inference.models.utils import (
    f_measure,
    tensor_all_reduce,
    tensor_all_gather,
)

logger = logging.getLogger(__name__)
logging.getLogger("shapely.geos").setLevel(logging.FATAL)


# Index 0 is Blank
# Index 1 is EOS
# Index 2 is 'Rare'
_NUM_SPECIAL = 3

# The maximum number of regions per batch that will be trained
MAX_REGIONS = 96


class UpdateTrainedStatsMessage(TargetEncoderMessage):
    def __init__(self, name, buffer: torch.Tensor):
        super().__init__(name)
        self.buffer = buffer

    def build_state(self, state):
        super().build_state(state)
        state["buffer"] = self.buffer


class RecognitionTargetEncoder(TargetEncoderBase):
    def __init__(
        self,
        charset: str,
        input_size,
        sequence_length: int,
        amp_opt=0,
        combine_duplicates=False,
        is_train=True,
        lm_path=None,
        verbose=False,
    ):
        super().__init__(input_size, amp_opt, verbose)

        self.sequence_length = sequence_length
        self.combine_duplicates = combine_duplicates
        self.is_train = is_train

        logger.info("Combine duplicates: {}".format(combine_duplicates))

        self.charset = charset
        self.lm_path = lm_path
        self.cpp_token_mapping = None

        self._initialized = False

        self.beam_lm = None

        self.send_buffers = None

    def _initialize(self):
        if self._initialized:
            return
        self._initialized = True

        self.idx_to_char = {i + _NUM_SPECIAL: c for i, c in enumerate(self.charset)}

        self.char_to_idx = {c: i + _NUM_SPECIAL for i, c in enumerate(self.charset)}

        if self.lm_path is not None:
            if not os.path.exists(self.lm_path):
                raise ValueError(f"The language model path '{self.lm_path}' doesn't exist!")
            self.beam_lm = create_sbo_lm(self.lm_path, self.idx_to_char)

        self.cpp_token_mapping = create_token_mapping(self.idx_to_char)

    def __getstate__(self):
        ret = dict(self.__dict__)
        if self._initialized:
            del ret["cpp_token_mapping"]
            del ret["idx_to_char"]
            del ret["char_to_idx"]
            del ret["beam_lm"]
            del ret["send_buffers"]
        ret["_initialized"] = False

        return ret

    @property
    def charset_size(self):
        return _NUM_SPECIAL + len(self.charset)

    def is_recognition(self):
        return True

    def get_charset(self):
        return self.charset

    def cb_convert_labels_to_targets(
        self, batch: tr.Batch, input_sizes, handle_region: Callable[[int, int, tr.TextRegion], None]
    ):
        self._initialize()

        # classes = []
        # masks = []
        region_counts = []
        geo_idxs = []
        word_lens = []
        word_use_counts = []

        additional = self.get_additional_regions(batch, input_sizes)

        # Get an upper bound for the number of regions, and the maximum text length
        loose_max_seq_len = 0
        loose_num_regions = 0
        for ex_idx, example in enumerate(batch):
            loose_num_regions += len(additional[ex_idx])
            for region in example:
                if region.valid:
                    loose_max_seq_len = max(loose_max_seq_len, len(region.text))
                    loose_num_regions += 1

        class_tensor = torch.empty(loose_num_regions, loose_max_seq_len + 1, dtype=torch.int64)
        mask_tensor = torch.empty(loose_num_regions, loose_max_seq_len + 1, dtype=torch.float32)

        max_seq_len = 0
        enc_offset = 0
        for ex_idx, example in enumerate(batch):
            regions = list(example.regions)

            if self.is_train:
                regions.extend(additional[ex_idx])

            used_regions = []
            for r_idx, region in enumerate(regions):
                valid = self.is_region_valid(region, used_regions)

                if not valid:
                    continue

                text = region.text

                max_seq_len = max(max_seq_len, len(text) + 1)
                enc_offset += 1

                word_lens.append(len(text))

                geo_idxs.append((ex_idx, r_idx))

                handle_region(ex_idx, r_idx, region)

                used_regions.append(region)
            region_counts.append(len(used_regions))

        class_tensor = class_tensor[:enc_offset, :max_seq_len]
        mask_tensor = mask_tensor[:enc_offset, :max_seq_len]

        region_counts = torch.tensor(region_counts, dtype=torch.int64)
        word_lens = torch.tensor(word_lens, dtype=torch.int32)

        if geo_idxs:
            geo_idxs = torch.tensor(geo_idxs, dtype=torch.int64)
        else:
            geo_idxs = torch.empty(0, 2, dtype=torch.int64)

        return {
            "sequences": class_tensor,
            "mask": mask_tensor,
            "region_counts": region_counts,
            "geo_idxs": geo_idxs,
        }

    def get_additional_regions(self, batch: tr.Batch, input_sizes):
        additional = [[] for _ in batch]
        if self.is_train:
            num_regions = sum(len(ex) for ex in batch)
            dummy_quads = self.create_dummy_quads(input_sizes[0], num_regions, len(batch))
            # Weight the probability of an example by the inverse of the number of regions.
            # Effectively, this means that examples with fewer regions are more likely
            # to get a dummy example
            probs = [(1 / len(ex)) if len(ex) > 0 else 2 for ex in batch]
            t_prob = sum(probs)
            probs = [p / t_prob for p in probs]
            assignments = np.random.choice(len(batch), size=len(dummy_quads), p=probs)
            for dummy, assign in zip(dummy_quads, assignments):
                additional[assign].append(dummy)
        return additional

    def is_region_valid(
        self, region: tr.TextRegion, used_regions: Optional[List[tr.TextRegion]] = None
    ):
        if not region.valid:
            return False

        if region.region.vertices.shape[0] < 4:
            return False

        try:
            region_area = region.region.area
            if region_area < 1:
                return False
        except:  # noqa: E722
            return False

        valid = True
        valid = valid and all(c in self.char_to_idx for c in region.text)
        valid = valid and getattr(region, "recog_valid", True)

        # This is one of our dummy / negative regions. For this, just ensure that it doesn't
        # intersect with other valid regions
        if valid and region.text == "" and used_regions is not None:
            for used_region in used_regions:
                if used_region.region._poly.intersects(region.region._poly):
                    valid = False
                    break

        return valid

    def limit_regions(
        self,
        targets: Dict[str, torch.Tensor],
        select_fn: Callable[[torch.Tensor, torch.Tensor], None],
        max_regions=MAX_REGIONS,
    ):
        in_region_counts = targets["region_counts"]
        word_use_counts = targets["word_use_counts"]

        # Partly as a training optimization, and partly to ensure that we have a bounded
        # memory envelope, train recognition with an upper bounded number of regions.
        # To do this, we sample from the full set of regions.
        if not self.is_train or word_use_counts.shape[0] <= max_regions:
            return

        inv_uses = 1 / word_use_counts.float()

        sel_indices = torch.multinomial(inv_uses, max_regions, replacement=False)
        sel_indices = torch.sort(sel_indices).values

        key_set = ["sequences", "mask", "geo_idxs"]

        in_buffers = [targets[k] for k in key_set]

        out_region_counts, out_buffers = sparse_select(in_region_counts, in_buffers, sel_indices)

        select_fn(in_region_counts, sel_indices)

        for k, v in zip(key_set, out_buffers):
            targets[k] = v
        targets["region_counts"] = out_region_counts

    def cb_convert_targets_to_labels(
        self,
        target_dict: Dict[str, torch.Tensor],
        image_size,
        limit_idxs: Optional[torch.Tensor],
        is_gt,
        subsel_fn: Optional[Callable[[int, int, int], Dict[str, torch.Tensor]]],
        geometry_fn: Callable[[Dict, int, int, int], torch.Tensor],
        **kwargs,
    ):
        self._initialize()

        target_dict = self.subselect_targets(target_dict, limit_idxs, subsel_fn)

        sequences = target_dict["sequences"].cpu()
        region_counts = target_dict["region_counts"].cpu()
        confidence = target_dict.get("confidence", None)
        if confidence is not None:
            confidence = confidence.cpu()

        decoded_seq_probs = None
        combine_duplicates = not is_gt and self.combine_duplicates
        language_model = self.beam_lm if not is_gt else None
        if sequences.dim() == 3:
            if sequences.shape[0] > 0:
                decoded_seq_ids, decoded_seq_probs, combine_duplicates = self.convert_preds_to_idxs(
                    sequences, combine_duplicates, language_model
                )
            else:
                decoded_seq_ids = torch.empty(
                    0, sequences.shape[1], dtype=torch.int64, device=sequences.device
                )
        elif sequences.dim() == 2:
            decoded_seq_ids = sequences
        else:
            raise ValueError("Unsupported sequence tensor!")

        decoded_strings = decode_sequences(
            decoded_seq_ids, self.cpp_token_mapping, decoded_seq_probs
        )

        examples = []
        offset = 0
        for ex_idx, region_count in enumerate(region_counts):
            region_count = region_count.item()

            regions = []
            for i in range(region_count):
                text, text_conf = decoded_strings[offset]
                region_conf = confidence[offset].item() if confidence is not None else 1
                geo = geometry_fn(target_dict, ex_idx, i, offset)
                offset += 1

                overall_conf = f_measure(region_conf, text_conf)

                region = tr.TextRegion(
                    Quadrangle(geo), text, valid=len(text) > 0 and overall_conf > 0.5
                )
                region.quad_prob = region_conf
                region.text_prob = text_conf
                region.confidence = overall_conf
                regions.append(region)

            examples.append(tr.Example(regions))

        return tr.Batch(examples)

    def subselect_targets(
        self,
        target_dict: Dict[str, torch.Tensor],
        limit_idxs: torch.Tensor,
        limit_fn: Optional[Callable[[int, int, int], Dict[str, torch.Tensor]]] = None,
    ):
        if limit_idxs is None:
            return target_dict

        sequences = target_dict["sequences"].cpu()
        region_counts = target_dict["region_counts"].cpu()
        geo_idxs = target_dict["geo_idxs"].cpu()
        confidence = target_dict.get("confidence", None)
        if confidence is not None:
            confidence = confidence.cpu()

        new_seqs = []
        new_counts = []
        new_confidence = []
        new_geo_idxs = []
        other_limits = defaultdict(lambda: [])
        cs_region_counts = torch.cumsum(region_counts, 0)
        for limit_idx in limit_idxs:
            limit_idx = limit_idx.item()
            start_offset = cs_region_counts[limit_idx - 1].item() if limit_idx > 0 else 0
            end_offset = cs_region_counts[limit_idx].item()
            new_seqs.append(sequences[start_offset:end_offset])
            new_geo_idxs.append(geo_idxs[start_offset:end_offset])

            if limit_fn is not None:
                others = limit_fn(limit_idx, start_offset, end_offset)
                for k, v in others.items():
                    other_limits[k].append(v)

            if confidence is not None:
                new_confidence.append(confidence[start_offset:end_offset])
            new_counts.append(region_counts[limit_idx].item())

        sequences = torch.cat(new_seqs)
        geo_idxs = torch.cat(new_geo_idxs)
        if confidence is not None:
            confidence = torch.cat(new_confidence)
        region_counts = torch.tensor(new_counts, dtype=torch.int64)
        for k, v in other_limits.items():
            other_limits[k] = torch.cat(v, dim=0)

        ret = {k: v for k, v in target_dict.items()}
        ret.update(
            sequences=sequences,
            region_counts=region_counts,
            geo_idxs=geo_idxs,
            confidence=confidence,
        )
        ret.update(other_limits)

        return ret

    def create_dummy_quads(self, input_size, num_curr_quads, batch_size):
        # num_quads = max(1, min(num_curr_quads // 10, 2 * batch_size))
        num_quads = batch_size

        quads = []
        for _ in range(num_quads):
            # Sample a centerpoint from the inner 3/4 of the image
            center = np.random.rand(2)
            center[0] = center[0] * (3 * input_size[-1] / 4) + (input_size[-1] / 8)
            center[1] = center[1] * (3 * input_size[-2] / 4) + (input_size[-2] / 8)

            # Sample an angle in the range of +/- pi/4
            angle = math.pi * (np.random.rand() * 2 - 1) / 4

            rot_mat = np.array(
                [[math.cos(angle), math.sin(angle)], [-math.sin(angle), math.cos(angle)]]
            ).T

            w = np.random.rand() * (input_size[-1] / 8)
            h = np.random.rand() * (input_size[-2] / 8)

            vecs = np.array(
                [
                    [-w, -h],
                    [w, -h],
                    [w, h],
                    [-w, h],
                ]
            )

            vecs = vecs.dot(rot_mat)

            vecs += center[None, :]

            # Clamp the quad to be within the image
            vecs[:, 0] = np.minimum(np.maximum(vecs[:, 0], 0), input_size[-1])
            vecs[:, 1] = np.minimum(np.maximum(vecs[:, 1], 0), input_size[-2])

            quads.append(torch.from_numpy(vecs))

        rand_coords = torch.stack(quads).float()

        return [tr.TextRegion(Quadrangle(coords), "", valid=True) for coords in rand_coords]

    @staticmethod
    def convert_preds_to_idxs(
        seq: torch.Tensor, combine_duplicates=False, language_model=None
    ) -> Tuple[torch.Tensor, torch.Tensor, bool]:
        """
        Converts a prediction distribution to the set of preferred sequences.
        seq: BxTxC, where B=batch, T=timestep, C=char
        Returns: Tuple[indices,probs]
        """

        if combine_duplicates or language_model is not None:
            ###### CTC
            output, scores = beam_decode(
                seq,
                100,
                lang_model=language_model,
                lm_weight=1,
                combine_duplicates=combine_duplicates,
            )
            ######
        else:
            ###### Max
            scores, output = torch.max(seq, dim=2)
            ######

        return output, scores, False

    def decode_sequence(
        self, seq: torch.Tensor, remove_duplicates=False, probs: torch.Tensor = None
    ) -> Tuple[str, float]:
        self._initialize()

        text = ""
        prev = None
        prob = 0
        for i, tok_idx in enumerate(seq):
            tok_idx = tok_idx.item()
            if tok_idx == prev and remove_duplicates:
                continue
            prev = tok_idx

            if tok_idx != 1 and probs is not None and probs.dim() == 1:
                tok_prob = math.log(probs[i].item())

                prob += tok_prob

            if tok_idx == 0:
                continue
                # text += '_'
            elif tok_idx == 1:
                break
            elif tok_idx == 2:
                text += "^"
            else:
                text += self.idx_to_char[tok_idx]

        prob = math.exp(prob)
        if probs is not None and probs.dim() == 0:
            prob = probs.item()
        # logger.info(f'Sequence: {text} - {prob}')
        return text, prob

    def send_messages(self, worker_comm_context, gpu_targets, name, **kwargs):
        recog_sequences = gpu_targets["sequences"]

        # Figure out a shape envelope for all of the sequences
        shape_tensor = torch.tensor(recog_sequences.shape, dtype=torch.int64, device="cpu")
        shape_tensor = tensor_all_reduce(shape_tensor, torch.distributed.ReduceOp.MAX)
        pad_sequences = torch.ones(
            *shape_tensor.tolist(), dtype=recog_sequences.dtype, device=recog_sequences.device
        )
        pad_sequences[: recog_sequences.shape[0], : recog_sequences.shape[1]] = recog_sequences
        pad_sequences[recog_sequences.shape[0] :, 0] = -1

        pad_sequences = tensor_all_gather(pad_sequences)
        vmask = pad_sequences[:, 0] != -1
        pad_sequences = pad_sequences[vmask].short()

        if self.send_buffers is None:
            self.send_buffers = deque(None for _ in range(worker_comm_context.num_workers + 1))

    def _convert_labels_to_targets(self, batch: tr.Batch, input_sizes):
        quads = []
        rrects = []

        def handle_region(ex_idx: int, r_idx: int, region: tr.TextRegion):
            rrect = region.region.min_rrect
            vtx_count = region.region.vertices.shape[0]
            if vtx_count == 4:
                quads.append(region.region.vertices)
            else:
                quads.append(rrect)
            rrects.append(rrect)

        ret = self.cb_convert_labels_to_targets(batch, input_sizes, handle_region)

        classes = ret["sequences"]
        if classes.shape[0] > 0:
            quad_tensor = torch.stack(quads)
            rrect_tensor = torch.stack(rrects)
        else:
            quad_tensor = torch.empty(0, 4, 2, dtype=torch.float32)
            rrect_tensor = torch.empty(0, 4, 2, dtype=torch.float32)

        ret.update(quads=quad_tensor, rboxes=rrect_tensor)

        def handle_select(region_counts: torch.Tensor, sel_indices: torch.Tensor):
            key_set = ["quads", "rboxes"]
            in_buffers = [ret[k] for k in key_set]

            _, out_buffers = sparse_select(region_counts, in_buffers, sel_indices)

            for k, v in zip(key_set, out_buffers):
                ret[k] = v

        self.limit_regions(ret, handle_select)

        ret["trained_quads"] = ret["quads"].clone()

        return ret

    def convert_targets_to_labels(
        self, target_dict, image_size, limit_idxs=None, is_gt=True, **kwargs
    ):
        def subsel_quads(limit_idx: int, start_offset: int, end_offset: int):
            return {"quads": target_dict["quads"][start_offset:end_offset]}

        def get_quad(target_dict: Dict[str, torch.Tensor], ex_idx: int, r_idx: int, r_offset: int):
            return target_dict["quads"][r_offset].cpu()

        return self.cb_convert_targets_to_labels(
            target_dict, image_size, limit_idxs, is_gt, subsel_fn=subsel_quads, geometry_fn=get_quad
        )
