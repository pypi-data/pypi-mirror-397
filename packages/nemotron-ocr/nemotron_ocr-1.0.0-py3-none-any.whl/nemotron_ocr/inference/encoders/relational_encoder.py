#!/usr/bin/env python
# -*- coding: utf-8 -*-

# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0


"""Multiple prior target encoder."""

import logging
import math

import torch

from nemotron_ocr.inference.post_processing.data.quadrangle import Quadrangle
import nemotron_ocr.inference.post_processing.data.text_region as tr
from nemotron_ocr.inference.encoders.base import TargetEncoderBase
from nemotron_ocr.inference.models.utils import cat

from nemotron_ocr_cpp import dense_relations_to_graph as cpp_dense_relations_to_graph

logger = logging.getLogger(__name__)
logging.getLogger("shapely.geos").setLevel(logging.FATAL)


class RelationalTargetEncoder(TargetEncoderBase):
    def __init__(self, input_size, amp_opt=0, is_train=True):
        super().__init__(input_size, amp_opt, False)

        self.is_train = is_train

    def _convert_labels_to_targets(self, batch: tr.Batch, input_sizes):
        all_relations = []
        all_line_relations = []
        all_weights = []
        all_region_valid = []
        all_relation_valid = []
        all_quads = []
        all_rrects = []
        all_ex_valid = []
        all_w_idx_to_line_map = []
        all_line_to_line_map = []
        geo_idxs = []
        r_offset = []
        region_counts = []

        for ex_idx, example in enumerate(batch):
            r_offset.append(len(geo_idxs))
            graph = example.relation_graph

            all_ex_valid.append(graph is not None)

            (
                relations,
                region_valid,
                relation_valid,
                line_relations,
                w_idx_to_line_map,
                line_to_line_map,
            ) = self.encode_relations(example, graph)

            all_relations.append(relations)
            all_region_valid.append(region_valid)
            all_relation_valid.append(relation_valid)
            all_line_relations.append(line_relations)
            all_w_idx_to_line_map.append(w_idx_to_line_map)
            all_line_to_line_map.append(line_to_line_map)
            region_counts.append(len(example))

            quads = []
            rrects = []
            for r_idx, region in enumerate(example):
                rrect, quad = self.get_rrect_and_quad(region)

                quads.append(quad)
                rrects.append(rrect)
                geo_idxs.append((ex_idx, r_idx))

            if not quads:
                quads = torch.empty(0, 4, 2, dtype=torch.float32)
                rrects = torch.empty(0, 4, 2, dtype=torch.float32)
            else:
                quads = torch.stack(quads)
                rrects = torch.stack(rrects)

            all_quads.append(quads)
            all_rrects.append(rrects)

        def get_offsets(rels):
            offsets = [0]
            for rel in rels:
                offsets.append(offsets[-1] + (0 if rel is None else rel.numel()))
            return offsets

        offsets = get_offsets(all_relations)

        offsets = torch.tensor(offsets, dtype=torch.int64)

        all_ex_valid = torch.tensor(all_ex_valid, dtype=torch.bool)

        r_offset.append(len(geo_idxs))
        geo_idxs = torch.tensor(geo_idxs)
        r_offset = torch.tensor(r_offset)
        region_counts = torch.tensor(region_counts)

        all_quads = cat(all_quads, 4, 2)
        all_rrects = cat(all_rrects, 4, 2)

        ret = {
            "ex_valid": all_ex_valid,
            "offsets": offsets,
            "relations": all_relations,
            "line_relations": all_line_relations,
            "weights": all_weights,
            "region_valid_mask": all_region_valid,
            "relation_valid_mask": all_relation_valid,
            "w_idx_to_line_map": all_w_idx_to_line_map,
            "line_to_line_map": all_line_to_line_map,
            "quads": all_quads,
            "rboxes": all_rrects,
            "ex_offsets": r_offset,
            "region_counts": region_counts,
            "geo_idxs": geo_idxs,
            "trained_quads": all_quads.clone(),
        }

        return ret

    def is_region_valid(self, region: tr.TextRegion):
        if not region.valid:
            return False

        if not getattr(region, "rel_valid", True):
            return False

        if region.region.vertices.shape[0] < 4:
            return False

        try:
            region_area = region.region.area

            if region_area <= 5:
                return False
        except:  # noqa: E722
            return False

        try:
            _ = region.region.min_rrect
        except:  # noqa: E722
            return False

        return True

    def encode_relations(self, example: tr.Example, graph: tr.RelationGraph):
        num_regions = len(example)
        relations = torch.full((num_regions,), -1, dtype=torch.int64)
        region_valid = torch.zeros(num_regions, dtype=torch.float32)
        relation_valid = torch.empty(num_regions, num_regions, dtype=torch.float32)
        line_relations = torch.zeros(num_regions, num_regions, dtype=torch.float32)

        num_lines = 0
        if graph is not None:
            graph = graph.split_lines(example)
            for para in graph.paragraphs:
                num_lines += len(para)

        w_idx_to_line_map = torch.empty(num_regions, dtype=torch.int64)
        line_to_line_map = torch.zeros(num_lines, num_lines, dtype=torch.float32)

        for i, region in enumerate(example):
            valid = self.is_region_valid(region)

            if valid:
                region_valid[i] = 1.0

        if graph is not None:
            # Invalidate all relations where the "from" is not valid
            relation_valid = region_valid[:, None] * region_valid[None, :]

            line_idx = 0
            for paragraph in graph.paragraphs:
                prev_sentence = None
                for sentence in paragraph:
                    if prev_sentence is not None:
                        for prev_word in prev_sentence:
                            for curr_word in sentence:
                                line_relations[prev_word, curr_word] = 1.0
                        line_to_line_map[line_idx - 1, line_idx] = 1.0

                    prev_word = None
                    for curr_word in sentence:
                        if prev_word is not None:
                            relations[prev_word] = curr_word
                        w_idx_to_line_map[curr_word] = line_idx
                        prev_word = curr_word
                    prev_sentence = sentence
                    line_idx += 1
            # Note: The `relation_valid` mask for lines is the outer product of region_valid and itself
        else:
            relation_valid.fill_(0)

        return (
            relations,
            region_valid,
            relation_valid,
            line_relations,
            w_idx_to_line_map,
            line_to_line_map,
        )

    def convert_targets_to_labels(
        self, target_dict, image_size, limit_idxs=None, is_gt=True, **kwargs
    ):
        all_word_relations = target_dict["relations"]
        all_line_relations = target_dict["line_relations"]
        all_line_unc = target_dict.get("line_rel_var", None)
        region_counts = target_dict["region_counts"].cpu()
        all_quads = target_dict["quads"]

        # These are ground truth. Convert them to dense form
        if all_word_relations[0].dim() == 1:
            all_word_relations = [sparse_to_dense(gt_rel) for gt_rel in all_word_relations]

        all_word_relations = [r.cpu() if r is not None else r for r in all_word_relations]
        all_line_relations = [r.cpu() if r is not None else r for r in all_line_relations]
        all_line_unc = (
            [r.cpu() if r is not None else r for r in all_line_unc]
            if all_line_unc is not None
            else None
        )
        region_counts = region_counts.cpu()
        all_quads = all_quads.cpu()
        cs_region_counts = torch.cumsum(region_counts, 0)

        examples = []
        for i, (word_relations, line_relations) in enumerate(
            zip(all_word_relations, all_line_relations)
        ):
            start_offset = cs_region_counts[i - 1] if i > 0 else 0
            end_offset = cs_region_counts[i]
            quads = all_quads[start_offset:end_offset]
            line_unc = all_line_unc[i] if all_line_unc is not None else None

            regions = [tr.TextRegion(Quadrangle(q), "") for q in quads]
            graph = None
            if end_offset > start_offset:
                graph = self.dense_relations_to_graph(
                    word_relations, line_relations, line_unc, is_gt
                )
            else:
                graph = tr.RelationGraph()

            ex = tr.Example(regions, relation_graph=graph)
            examples.append(ex)

        if limit_idxs is not None:
            examples = [examples[idx] for idx in limit_idxs]

        return tr.Batch(examples)

    def sparse_relations_to_graph(self, relations: torch.Tensor):
        relations = relations.cpu().tolist()

        in_chain = dict()
        for from_idx, to_idx in enumerate(relations):
            if to_idx == -1:
                continue

            in_chain[to_idx] = (from_idx, 1)

        sentences = self.in_chain_to_groups(in_chain, len(relations))
        paragraphs = [[s] for s in sentences]

        return tr.RelationGraph(paragraphs)

    def dense_relations_to_graph(
        self,
        word_relations: torch.Tensor,
        line_logits: torch.Tensor,
        line_log_uncertainty: torch.Tensor = None,
        is_gt=False,
    ):
        lines = [p[0] for p in cpp_dense_relations_to_graph(word_relations)]

        line_logits = line_logits.float()

        if is_gt:
            null_conn = (line_logits.sum(dim=1, keepdim=True) == 0).to(line_logits.dtype)
            line_logits = torch.cat((null_conn, line_logits), dim=1)

        if line_log_uncertainty is not None:
            line_log_uncertainty = line_log_uncertainty.float()
            inv_uncertainty = torch.exp(-line_log_uncertainty)
        else:
            inv_uncertainty = torch.ones_like(line_logits)

        w_idx_to_line_map = torch.empty(word_relations.shape[0], dtype=torch.int64)

        line_idx = 0
        for line in lines:
            for word in line:
                w_idx_to_line_map[word] = line_idx
            line_idx += 1

        valid_mask = line_logits != -math.inf

        null_w_idx_to_line_map = torch.cat(
            (torch.tensor([0], dtype=w_idx_to_line_map.dtype), w_idx_to_line_map + 1), dim=0
        )

        sa_w2l_idxs = null_w_idx_to_line_map.reshape(1, -1).expand(w_idx_to_line_map.shape[0], -1)
        sa_l2l_idxs = w_idx_to_line_map.reshape(-1, 1).expand(-1, line_idx + 1)

        line_logits = torch.where(valid_mask, line_logits, torch.zeros_like(line_logits))
        inv_uncertainty = torch.where(
            valid_mask, inv_uncertainty, torch.zeros_like(inv_uncertainty)
        )

        word_to_line_unc = torch.zeros(
            w_idx_to_line_map.shape[0], line_idx + 1, dtype=line_logits.dtype
        )
        word_to_line_unc.scatter_add_(dim=1, index=sa_w2l_idxs, src=inv_uncertainty)

        line_to_line_unc = torch.zeros(line_idx, line_idx + 1, dtype=line_logits.dtype)
        line_to_line_unc.scatter_add_(dim=0, index=sa_l2l_idxs, src=word_to_line_unc)

        # The first index will give us the total of going from a word to a line, and the second gives us going from one word to another
        unc_sums = line_to_line_unc[w_idx_to_line_map][:, null_w_idx_to_line_map].clamp_min(1e-6)

        unc_weights = inv_uncertainty / unc_sums

        w_logits = torch.where(valid_mask, unc_weights * line_logits, torch.zeros_like(line_logits))

        word_to_line_logits = torch.zeros_like(word_to_line_unc)
        word_to_line_logits.scatter_add_(dim=1, index=sa_w2l_idxs, src=w_logits)

        line_to_line_logits = torch.zeros_like(line_to_line_unc)
        line_to_line_logits.scatter_add_(dim=0, index=sa_l2l_idxs, src=word_to_line_logits)

        self_mask = torch.full(
            (line_to_line_logits.shape[0],), -math.inf, dtype=line_to_line_logits.dtype
        ).diag()
        self_mask = torch.cat(
            (torch.zeros(self_mask.shape[0], 1, dtype=self_mask.dtype), self_mask), dim=1
        )

        line_to_line_logits += self_mask

        line_to_line_probs = torch.softmax(line_to_line_logits, dim=1, dtype=torch.float32)
        line_maxes = torch.max(line_to_line_probs, dim=1, keepdim=True).values
        line_to_line_probs = torch.where(
            line_to_line_probs == line_maxes,
            torch.ones_like(line_to_line_probs),
            torch.zeros_like(line_to_line_probs),
        )
        line_to_line_probs = line_to_line_probs[:, 1:]

        rel_lines = set(tuple(p[0]) for p in cpp_dense_relations_to_graph(line_to_line_probs))

        paragraphs = []
        for rel_line in rel_lines:
            para = [lines[l_idx] for l_idx in rel_line]
            paragraphs.append(para)

        return tr.RelationGraph(paragraphs)

    def construct_paragraphs(self, sentences, paragraphs):
        word_to_sentence = dict()
        for s in sentences:
            for word_idx in s:
                word_to_sentence[word_idx] = s

        new_paragraphs = []
        proc_ids = set()
        for para in paragraphs:
            new_para = []
            for word_idx in para:
                s = word_to_sentence[word_idx]

                if s not in new_para:
                    new_para.append(s)
            if all(proc_ids.isdisjoint(s) for s in new_para):
                for s in new_para:
                    proc_ids.update(s)
                new_paragraphs.append(new_para)

        return new_paragraphs

    def cvt_to_1_hot(self, relations: torch.Tensor):
        if relations.dim() == 3:
            return relations

        one_hot = torch.eye(3, dtype=torch.float32, device=relations.device)

        f_rel = relations.reshape(-1)

        oh_f_rel = one_hot[f_rel]

        oh_rel = oh_f_rel.reshape(*relations.shape, -1)

        return oh_rel

    def in_chain_to_groups(self, in_chain: dict, num_regions: int):
        out_chain = {v[0]: k for k, v in in_chain.items()}

        processed = set()
        groups = []
        for to_idx, (from_idx, conf) in in_chain.items():
            if to_idx in processed:
                continue

            # Find the start of the chain
            cycle_set = {from_idx}
            is_cycle = False
            while from_idx in in_chain:
                to_idx = from_idx
                from_idx = in_chain[to_idx][0]
                if from_idx in cycle_set:
                    is_cycle = True
                    break

            # Completely ignore cycle chains
            if is_cycle:
                continue

            group = [from_idx]
            processed.add(from_idx)
            while to_idx in out_chain:
                processed.add(to_idx)
                group.append(to_idx)
                to_idx = out_chain[to_idx]
            group.append(to_idx)
            processed.add(to_idx)

            groups.append(group)

        # Now add in the stragglers
        for w_idx in range(num_regions):
            if w_idx not in processed:
                groups.append([w_idx])

        return groups


def sparse_to_dense(sparse: torch.Tensor, handle_invalid=True, encode_null=False):
    cols = sparse.shape[0]
    if encode_null:
        sparse = sparse + 1
        cols += 1

    rel_valid_mask = None
    ones = torch.ones(sparse.shape[0], dtype=torch.float32, device=sparse.device)
    if handle_invalid:
        rel_valid_mask = torch.where(sparse >= 0, ones, torch.zeros_like(ones))

    if not encode_null:
        sparse = sparse.clamp_min(0)

    dense = torch.zeros(sparse.shape[0], cols, dtype=torch.float32, device=sparse.device)
    dense.scatter_(dim=1, index=sparse.unsqueeze(1), src=ones.unsqueeze(1))

    if rel_valid_mask is not None:
        dense *= rel_valid_mask[:, None]
    return dense
