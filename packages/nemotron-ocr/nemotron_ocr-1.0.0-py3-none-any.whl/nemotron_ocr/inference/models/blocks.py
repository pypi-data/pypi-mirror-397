# SPDX-FileCopyrightText: Copyright (c) 2025, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

"""Model blocks."""

import logging
import math

import torch
import torch.nn as nn
import torch.nn.functional as F

logger = logging.getLogger(__name__)


class CReLU(nn.Module):
    def __init__(self, act=F.relu):
        super().__init__()

        self.act = act

    def forward(self, x):
        x = torch.cat((x, -x), dim=1)
        x = self.act(x)
        return x


def get_activation(name):
    """Returns a pytorch activation layer of type 'name', where 'name' is a string."""
    if isinstance(name, nn.Module):
        return name

    if name == "relu":
        return nn.ReLU()
    if name == "elu":
        return nn.ELU()
    if name == "selu":
        return nn.SELU()
    if name == "sigmoid":
        return nn.Sigmoid()
    if name == "tanh":
        return nn.Tanh()
    if name == "softplus":
        return nn.Softplus()
    if name == "crelu":
        return CReLU()
    if name == "none":
        return None
    raise ValueError(
        "Unsupported activation type: {}. " "Ensure activation name is all lower case.".format(name)
    )


def conv2d_block(
    in_channels,
    out_channels,
    kernel_size,
    stride=1,
    padding=0,
    dilation=1,
    groups=1,
    bias=True,
    padding_mode="zeros",
    activation="relu",
    batch_norm=True,
):
    """
    Returns pytorch two-dimensional convolutional layer with activation and batch_norm if requested.

    Args:
        in_channels (int): number of input channels.
        out_channels (int): number of output channels.
        kernel_size (int): height and width of kernels.
        stride (int): stride of the filters, default=1.
        padding (int): padding added to input height x width, default=0.
        dilation (int): dilation factor, default=1.
        groups (int): number of convolution groups, default=1.
        bias (bool): whether to use bias, default=True.
        padding_mode (string): mode for applying padding, default='zeros'.
        activation (string): type of activation, default='relu'.
        batch_norm (bool): whether to use batch normalization, default=True.

    Returns:
        conv2d_layer (nn.Sequential): pytorch two-dimensional convolution layer.
    """
    items = [
        nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride=stride,
            padding=padding,
            dilation=dilation,
            groups=groups,
            bias=bias,
            padding_mode=padding_mode,
        ),
    ]

    if batch_norm:
        items.append(nn.BatchNorm2d(out_channels))

    act = get_activation(activation)
    if act:
        items.append(act)

    return nn.Sequential(*items)


class ResBlock(nn.Module):
    def __init__(self, in_channels, out_channels, activation="relu", batch_norm=True):
        super().__init__()

        self.batch_norm = batch_norm

        self.conv1 = nn.Conv2d(in_channels, out_channels, 3, padding=1)
        self.conv2 = nn.Conv2d(out_channels, out_channels, 3, padding=1)

        self.downsample = None
        if in_channels != out_channels:
            self.downsample = nn.Conv2d(in_channels, out_channels, 1)

        self.bn1 = nn.BatchNorm2d(out_channels)
        self.bn2 = nn.BatchNorm2d(out_channels)
        self.act = get_activation(activation)

    def forward(self, x):
        identity = x

        out = self.conv1(x)
        if self.batch_norm:
            out = self.bn1(out)
        out = self.act(out)

        out = self.conv2(out)
        if self.batch_norm:
            out = self.bn2(out)

        if self.downsample is not None:
            identity = self.downsample(identity)

        out = out + identity

        return self.act(out)


class Residual(nn.Module):
    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def forward(self, x: torch.Tensor):
        y = self.inner(x)
        return x + y


def initialize_weights(model):
    """Initializes the model weights."""
    for m in model.modules():
        if isinstance(m, (torch.nn.Conv2d, torch.nn.Linear)):
            torch.nn.init.kaiming_uniform_(m.weight, mode="fan_out", nonlinearity="relu")


def get_no_bias_decay_params(model, l2_value):
    """Returns weight decay parameters; l2_value set as the weight decay for layers with decay."""
    decay, no_decay = [], []
    for name, param in model.named_parameters():
        if not param.requires_grad:
            continue

        if name.endswith("bias"):
            no_decay.append(param)
        else:
            decay.append(param)

    return [{"params": no_decay, "weight_decay": 0.0}, {"params": decay, "weight_decay": l2_value}]


class GCContext(nn.Module):
    def __init__(self, input_dim):
        super().__init__()

        self.input_dim = input_dim

        self.key_proj = nn.Conv2d(input_dim, 1, 1)

    def forward(self, x):
        # B,C,H,W

        attn = self.key_proj(x) / math.sqrt(self.input_dim)
        # B,1,H,W
        attn = attn.reshape(x.shape[0], 1, -1)
        # B,1,HW
        attn = F.softmax(attn, dim=-1, dtype=torch.float32)
        attn = attn.reshape(x.shape[0], -1, 1)
        # B,HW,1

        rs_x = x.reshape(x.shape[0], x.shape[1], -1)
        # B,C,HW

        focus = torch.bmm(rs_x, attn)
        # B,C,1
        focus = focus.reshape(x.shape[0], x.shape[1], 1, 1)
        # B,C,1,1

        return focus


class GCTransform(nn.Module):
    def __init__(self, input_dim, bottleneck_dim):
        super().__init__()

        self.input_dim = input_dim
        self.bottleneck_dim = bottleneck_dim

        self.conv_encode = nn.Conv2d(input_dim, bottleneck_dim, 1)
        self.norm = nn.LayerNorm([bottleneck_dim, 1, 1])
        self.conv_decode = nn.Conv2d(bottleneck_dim, input_dim, 1)

    def forward(self, context):
        encoded = self.conv_encode(context)
        # B,R,1,1

        encoded = self.norm(F.relu(encoded))

        decoded = self.conv_decode(encoded)
        # B,C,1,1

        return decoded


class GCAttention(nn.Module):
    def __init__(self, input_dim, bottleneck_dim):
        super().__init__()

        self.context = GCContext(input_dim)
        self.transform = GCTransform(input_dim, bottleneck_dim)

    def forward(self, x):
        context = self.context(x)

        tx = self.transform(context)

        ret = x + tx

        return ret


class MAGCContext(nn.Module):
    def __init__(self, input_dim, num_aspects):
        super().__init__()

        if input_dim % num_aspects != 0:
            raise ValueError("Number of aspects must evenly divide input_dim!")

        self.input_dim = input_dim
        self.num_aspects = num_aspects

        self.split_size = input_dim // num_aspects

        self.key_proj = nn.Conv2d(input_dim, num_aspects, 1, groups=num_aspects)

    def forward(self, x):
        # x: B,C,H,W

        # B,A,H,W
        attn = self.key_proj(x) / math.sqrt(self.split_size)
        # B,A,HW
        attn = attn.reshape(attn.shape[0], attn.shape[1], -1)
        attn_probs = F.softmax(attn, dim=2, dtype=torch.float32)
        # B,A,1,HW
        attn_probs = attn_probs.unsqueeze(dim=2)

        # B,A,C/A,HW
        rs_x = x.reshape(x.shape[0], self.num_aspects, self.split_size, -1)
        # B,A,HW,C/A
        rs_x = rs_x.permute(0, 1, 3, 2)

        # B,A,1,C/A
        focus = torch.matmul(attn_probs, rs_x)

        # B,C,1,1
        return focus.reshape(focus.shape[0], -1, 1, 1)


class MAGCAttention(nn.Module):
    def __init__(self, input_dim, num_aspects, bottleneck_dim):
        super().__init__()

        self.context = MAGCContext(input_dim, num_aspects)

        self.transform = GCTransform(input_dim, bottleneck_dim)

    def forward(self, x):
        context = self.context(x)

        tx = self.transform(context)

        ret = x + tx

        return ret


class mCReLU_base(nn.Module):
    def __init__(self, n_in, n_out, kernel_size, stride=1, pre_act=False, last_act=True):
        super().__init__()

        self.pre_act = pre_act
        self.last_act = last_act
        self.act = F.relu

        self.conv = nn.Conv2d(n_in, n_out, kernel_size, stride=stride, padding=kernel_size // 2)
        self.bn = nn.BatchNorm2d(n_out * 2)

    def forward(self, x):
        if self.pre_act:
            x = self.act(x)

        x = self.conv(x)
        x = torch.cat((x, -x), dim=1)
        x = self.bn(x)

        if self.last_act:
            x = self.act(x)

        return x


class mCReLU_residual(nn.Module):
    def __init__(
        self,
        n_in,
        n_red,
        n_kernel,
        n_out,
        kernel_size=3,
        in_stride=1,
        proj=False,
        pre_act=False,
        last_act=True,
    ):
        super().__init__()

        self.pre_act = pre_act
        self.last_act = last_act
        self.stride = in_stride
        self.act = F.relu

        self.reduce = nn.Conv2d(n_in, n_red, 1, stride=in_stride)
        self.conv = nn.Conv2d(n_red, n_kernel, kernel_size, padding=kernel_size // 2)
        self.bn = nn.BatchNorm2d(n_kernel * 2)
        self.expand = nn.Conv2d(n_kernel * 2, n_out, 1)

        if in_stride > 1:
            assert proj

        self.proj = nn.Conv2d(n_in, n_out, 1, stride=in_stride) if proj else None

    def forward(self, x):
        x_sc = x

        if self.pre_act:
            x = self.act(x)

        x = self.reduce(x)
        x = self.act(x)

        x = self.conv(x)
        x = torch.cat((x, -x), 1)
        x = self.bn(x)
        x = self.act(x)

        x = self.expand(x)

        if self.last_act:
            x = self.act(x)

        if self.proj:
            x_sc = self.proj(x_sc)

        x = x + x_sc

        return x


class Inception(nn.Module):
    def __init__(self, n_in, n_out, in_stride=1, preAct=False, lastAct=True, proj=False):
        super(Inception, self).__init__()

        # Config
        self._preAct = preAct
        self._lastAct = lastAct
        self.n_in = n_in
        self.n_out = n_out
        self.act_func = nn.ReLU
        self.act = F.relu
        self.in_stride = in_stride

        self.n_branches = 0
        self.n_outs = []  # number of output feature for each branch

        self.proj = nn.Conv2d(n_in, n_out, 1, stride=in_stride) if proj else None

    def add_branch(self, module, n_out):
        # Create branch
        br_name = "branch_{}".format(self.n_branches)
        setattr(self, br_name, module)

        # Last output chns.
        self.n_outs.append(n_out)

        self.n_branches += 1

    def branch(self, idx):
        br_name = "branch_{}".format(idx)
        return getattr(self, br_name, None)

    def add_convs(self, n_kernels, n_chns):
        assert len(n_kernels) == len(n_chns)

        n_last = self.n_in
        layers = []

        stride = -1
        for k, n_out in zip(n_kernels, n_chns):
            if stride == -1:
                stride = self.in_stride
            else:
                stride = 1

            # Initialize params
            conv = nn.Conv2d(
                n_last, n_out, kernel_size=k, bias=False, padding=int(k / 2), stride=stride
            )
            bn = nn.BatchNorm2d(n_out)

            # Instantiate network
            layers.append(conv)
            layers.append(bn)
            layers.append(self.act_func())

            n_last = n_out

        self.add_branch(nn.Sequential(*layers), n_last)

        return self

    def add_poolconv(self, kernel, n_out, type="MAX"):
        assert type in ["AVE", "MAX"]

        n_last = self.n_in
        layers = []

        # Pooling
        if type == "MAX":
            layers.append(nn.MaxPool2d(kernel, padding=int(kernel / 2), stride=self.in_stride))
        elif type == "AVE":
            layers.append(nn.AvgPool2d(kernel, padding=int(kernel / 2), stride=self.in_stride))

        # Conv - BN - Act
        layers.append(nn.Conv2d(n_last, n_out, kernel_size=1))
        layers.append(nn.BatchNorm2d(n_out))
        layers.append(self.act_func())

        self.add_branch(nn.Sequential(*layers), n_out)

        return self

    def finalize(self):
        # Add 1x1 convolution
        total_outs = sum(self.n_outs)

        self.last_conv = nn.Conv2d(total_outs, self.n_out, kernel_size=1)
        self.last_bn = nn.BatchNorm2d(self.n_out)

        return self

    def forward(self, x):
        x_sc = x

        if self._preAct:
            x = self.act(x)

        # Compute branches
        h = []
        for i in range(self.n_branches):
            module = self.branch(i)
            assert module is not None

            h.append(module(x))

        x = torch.cat(h, dim=1)

        x = self.last_conv(x)
        x = self.last_bn(x)

        if self._lastAct:
            x = self.act(x)

        if x_sc.get_device() != x.get_device():
            print("Something's wrong")

        # Projection
        if self.proj:
            x_sc = self.proj(x_sc)

        x = x + x_sc

        return x
