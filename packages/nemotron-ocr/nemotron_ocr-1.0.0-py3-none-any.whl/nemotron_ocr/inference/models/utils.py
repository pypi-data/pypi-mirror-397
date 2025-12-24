# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import logging
import os
from typing import Dict, Any

import torch

logger = logging.getLogger(__name__)


def is_named_tuple(obj):
    """
    Return where or not the specified instance is a namedtuple.

    NOTE: Not guaranteed to be correct, but close.

    Args:
        obj (object): Some object to test.
    """
    return isinstance(obj, tuple) and getattr(obj, "_fields", None) is not None


def find_checkpoint(checkpoint_path):
    checkpoint_path = os.path.join(checkpoint_path, "best_checkpoint.pth")

    return checkpoint_path


def cat(tensors, *rest_shape, dtype=torch.float32) -> torch.Tensor:
    if tensors:
        return torch.cat(tensors)
    else:
        return torch.empty(0, *rest_shape, dtype=dtype)


def options(tensor: torch.Tensor) -> Dict[str, Any]:
    """
    Returns as a dict the dtype and device options for a tensor. This allows you
    to construct a new tensor with a compatible format.

    e.g.
    new_tensor = torch.empty(<shape>, **options(other_tensor))
    """
    return {"dtype": tensor.dtype, "device": tensor.device}


def f_measure(*args):
    acc = 0
    for v in args:
        if torch.is_tensor(v):
            v = v.clamp_min(1e-8)
        elif v <= 0:
            v = 1e-8
        acc += 1.0 / v

    fmeasure = len(args) / acc

    return fmeasure


def tensor_all_reduce(tensor, reduce_op=torch.distributed.ReduceOp.SUM):
    if torch.distributed.is_initialized():
        was_cuda = tensor.is_cuda
        tensor = tensor.cuda(non_blocking=True)
        torch.distributed.all_reduce(tensor, reduce_op)
        if not was_cuda:
            tensor = tensor.cpu()
    return tensor


def tensor_all_gather(tensor: torch.Tensor, dim=0):
    if not torch.distributed.is_initialized():
        return tensor

    tensor = tensor.contiguous()
    orig_dtype = tensor.dtype
    if tensor.dtype == torch.bool:
        tensor = tensor.to(torch.int64)
    orig_device = tensor.device
    if not tensor.is_cuda:
        tensor = tensor.cuda(non_blocking=True)
    # Scalar tensor
    if len(tensor.shape) == 0:
        tensor = tensor.reshape(1)

    buffers = [torch.empty_like(tensor) for i in range(torch.distributed.get_world_size())]

    torch.distributed.all_gather(buffers, tensor)

    return torch.cat(buffers, dim=dim).to(dtype=orig_dtype, device=orig_device)
