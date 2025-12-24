# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Optional

import torch
import torch.nn as nn

from nemotron_ocr.inference.models import blocks

logger = logging.getLogger(__name__)


class TransformerRecognizer(nn.Module):
    def __init__(self, nic: int, num_tokens: int, max_width: int) -> None:
        super().__init__()
        self.num_tokens = num_tokens
        self.fixed_width = max_width > 0
        self.inference_mode = False
        depth = 128

        max_width = abs(max_width)

        final_depth = depth * 2

        self.feature_depth = final_depth

        CONV_SHAPE = (3, 3)
        PAD_SHAPE = tuple((c - 1) // 2 for c in CONV_SHAPE)

        self.encoder = nn.Sequential(
            blocks.conv2d_block(nic, nic, 3, padding=1),
            blocks.conv2d_block(nic, nic * 2, 3, padding=1),
            nn.MaxPool2d((2, 1)),
            blocks.conv2d_block(nic * 2, nic * 2, CONV_SHAPE, padding=PAD_SHAPE),
            blocks.conv2d_block(nic * 2, depth * 2, CONV_SHAPE, padding=PAD_SHAPE),
            nn.MaxPool2d((2, 1)),
            blocks.conv2d_block(depth * 2, final_depth, CONV_SHAPE, padding=PAD_SHAPE),
            blocks.conv2d_block(final_depth, final_depth * 2, CONV_SHAPE, padding=PAD_SHAPE),
            nn.MaxPool2d((2, 1)),
            blocks.conv2d_block(final_depth * 2, final_depth, 1),
        )

        self.position_encoding = nn.Parameter(torch.randn(1, final_depth, max_width))

        self.tx = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(final_depth, 8, final_depth, dropout=0.0, batch_first=True),
            num_layers=3,
        )
        self.classifier = nn.Linear(final_depth, num_tokens)

    def forward(self, x: torch.Tensor, cpu_region_counts: Optional[torch.Tensor] = None):
        x = self.encoder(x).squeeze(2)

        if self.fixed_width:
            pos = self.position_encoding
        else:
            pos = self.position_encoding[..., : x.shape[2]]
        x = x + pos

        # B,T,C
        x = x.permute(0, 2, 1).contiguous()

        x = self.tx(x)

        y = self.classifier(x)

        return y, x
