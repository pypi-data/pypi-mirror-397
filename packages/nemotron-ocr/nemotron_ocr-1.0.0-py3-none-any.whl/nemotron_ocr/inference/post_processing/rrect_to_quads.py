# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import torch
from torch.autograd import Function
from nemotron_ocr_cpp import rrect_to_quads, rrect_to_quads_backward


class RRectToQuadsFunction(Function):
    @staticmethod
    def forward(ctx, rrects: torch.Tensor, cell_size: float):
        ctx.save_for_backward(rrects)

        return rrect_to_quads(rrects, cell_size)

    @staticmethod
    def backward(ctx, grad_output: torch.Tensor):
        rrects = ctx.saved_variables[0]

        grad_input = rrect_to_quads_backward(rrects, grad_output)

        return grad_input, None


class RRectToQuads(torch.nn.Module):
    def __init__(self, cell_size: float):
        super().__init__()
        self.cell_size = cell_size

    def forward(self, rrects: torch.Tensor):
        return RRectToQuadsFunction.apply(rrects, self.cell_size)
