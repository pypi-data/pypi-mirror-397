# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import math

import torch
import torch.nn.functional as F


def pad_to_square(img: torch.Tensor, target_length: int, how="center") -> torch.Tensor:
    """
    Pads the input image to a square shape with the specified size.

    Args:
        img (torch.Tensor): Input image tensor of shape (C, H, W).
        size (int): The target size for both height and width.

    Returns:
        torch.Tensor: Padded image tensor of shape (C, size, size).
    """
    _, h, w = img.shape

    if how == "center":
        pad_h = (target_length - h) // 2
        pad_w = (target_length - w) // 2
        return F.pad(
            img, (pad_w, target_length - w - pad_w, pad_h, target_length - h - pad_h), value=1.0
        )
    elif how == "bottom_right":
        pad_h = target_length - h
        pad_w = target_length - w
        return F.pad(img, (0, pad_w, 0, pad_h), value=1.0)
    else:
        raise ValueError(f"Unsupported padding method: {how}")


def interpolate_and_pad(
    images: torch.Tensor, pad_color: torch.Tensor, infer_length: int
) -> torch.Tensor:
    """
    Interpolates the input images to a specified height and pads them to a specified width.

    Args:
        images (torch.Tensor): Input image tensor of shape (B, C, H, W).
        infer_height (int): The target height for interpolation.
        pad_infer_width (int): The target width for padding.

    Returns:
        torch.Tensor: Interpolated and padded image tensor of shape (B, C, infer_height, pad_infer_width).
    """
    pad_infer_width = int(math.ceil(infer_length / 128) * 128)

    rs_images = F.interpolate(
        images, size=(infer_length, infer_length), mode="bilinear", align_corners=True
    )

    padded = (
        pad_color.reshape(1, -1, 1, 1)
        .expand(images.shape[0], -1, infer_length, pad_infer_width)
        .contiguous()
    )
    padded[..., :infer_length].copy_(rs_images)

    return padded
