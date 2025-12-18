# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

from typing import List

import torch
from torch import Tensor

from subquadratic_ops_torch.utils import get_module


@torch.library.custom_op(
    "subquadratic_ops_torch::causal_conv1d_fwd_primitive",
    mutates_args=(),
    device_types="cuda",
)
def _(x: Tensor, weight: Tensor) -> Tensor:
    if x.dim() != 3 or weight.dim() != 2:
        raise ValueError(
            f"Input and weights must be 3D and 2D tensors, {x.shape}, {weight.shape}"
        )

    x = x.contiguous()
    weight = weight.contiguous()
    y = torch.empty((x.shape[0], x.shape[1], x.shape[2]),
                    device=x.device, dtype=x.dtype)

    module = get_module("causal_conv1d_fwd", [x.dtype])
    stream_id = torch.cuda.current_stream(x.device).stream_id
    module(y.detach(), x.detach(), weight.detach(), stream_id)

    return y


@torch.library.register_fake("subquadratic_ops_torch::causal_conv1d_fwd_primitive")
def _(x: Tensor, weight: Tensor) -> Tensor:
    return torch.empty_like(x)


@torch.library.custom_op(
    "subquadratic_ops_torch::causal_conv1d_bwd_primitive",
    mutates_args=(),
    device_types="cuda",
)
def _(grad_out: Tensor, x: Tensor, weight: Tensor) -> List[Tensor]:
    if x.dim() != 3 or weight.dim() != 2:
        raise ValueError(
            f"Input and weights must be 3D and 2D tensors, {x.shape}, {weight.shape}"
        )

    grad_out_y = grad_out

    grad_x = torch.empty(x.shape, device=x.device, dtype=x.dtype)
    grad_weight = torch.zeros(weight.shape, device=x.device,
                              dtype=torch.float32 if x.dtype.itemsize == 2 else x.dtype)
    module = get_module("causal_conv1d_bwd", [x.dtype])
    stream_id = torch.cuda.current_stream(x.device).stream_id

    x = x.contiguous()
    weight = weight.contiguous()
    grad_out_y = grad_out_y.contiguous()

    module(grad_x.detach(), grad_weight.detach(), grad_out_y.detach(),
           x.detach(), weight.detach(), stream_id)

    return [grad_x, grad_weight.to(x.dtype)]


@torch.library.register_fake("subquadratic_ops_torch::causal_conv1d_bwd_primitive")
def _(grad_out: Tensor, x: Tensor, weight: Tensor) -> List[Tensor]:
    return [torch.empty_like(x), torch.empty_like(weight)]


def causal_conv1d_fwd_setup_fwd_context(ctx, inputs, output):
    (x, weight) = inputs
    ctx.save_for_backward(x, weight)  # Save y_gated along with other tensors


@torch.compiler.allow_in_graph
def causal_conv1d_fwd(*args):
    return torch.ops.subquadratic_ops_torch.causal_conv1d_fwd_primitive(*args)


@torch.compiler.allow_in_graph
def causal_conv1d_bwd(ctx, grad_out):
    x, weight = ctx.saved_tensors

    dx, dw = torch.ops.subquadratic_ops_torch.causal_conv1d_bwd_primitive(grad_out, x, weight)
    return dx, dw


torch.library.register_autograd(
    "subquadratic_ops_torch::causal_conv1d_fwd_primitive",
    causal_conv1d_bwd,
    setup_context=causal_conv1d_fwd_setup_fwd_context,
)


def causal_conv1d(x: Tensor, weight: Tensor) -> Tensor:
    y = torch.ops.subquadratic_ops_torch.causal_conv1d_fwd_primitive(x, weight)
    return y
