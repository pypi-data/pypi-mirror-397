# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Data container containing uniform calls to data manipulation functions."""


class DataContainer(object):
    """
    Business object helper that allows for low-level data operations to be uniformly called.

    Essentially, this prevents us from having to write a wrapper call for low level objects.

    e.g. The `Path` object has two `Polyline`s which support these operations. By supporting the
    `__iter__` function, it means that it can inherit from this object instead of implementing
    and forwarding all of these calls to the `Polyline` object. Similarly, the `Example` object
    contains multiple `Path`s, and the `Batch` contains multiple `Example`s.
    """

    def __iter__(self):
        """Make iterable."""
        raise NotImplementedError("Subclasses must implement this!")

    def apply_stm(self, *args, **kwargs):
        """Applies the homogeneous transformation matrix."""
        for sub_item in self:
            sub_item.apply_stm(*args, **kwargs)

    def translate(self, *args, **kwargs):
        """Translates a set of vertices."""
        for sub_item in self:
            sub_item.translate(*args, **kwargs)

    def scale(self, *args, **kwargs):
        """Multiplies a set of vertices by a scale factor."""
        for sub_item in self:
            sub_item.scale(*args, **kwargs)

    def rotate(self, *args, **kwargs):
        for sub_item in self:
            sub_item.rotate(*args, **kwargs)

    def apply(self, fn):
        for sub_item in self:
            sub_item.apply(fn)

    def validate(self):
        return all(sub.validate() for sub in self)

    def mark_dirty(self):
        for sub_item in self:
            sub_item.mark_dirty()
