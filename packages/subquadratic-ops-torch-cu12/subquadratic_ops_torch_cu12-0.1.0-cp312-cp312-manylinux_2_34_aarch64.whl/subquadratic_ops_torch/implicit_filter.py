# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import torch
import warp as wp
from typing import List
from subquadratic_ops_torch._ext.utils import get_stream, get_warp_module, add_warp_module
from subquadratic_ops_torch._ext.kernel import generate_implicit_filter_kernels, IMPLICIT_FILTER_L_SEG_SIZE

wp.config.quiet = True
wp.init()


@torch.library.custom_op(
    "subquadratic_ops_torch::implicit_filter_fwd_primitive",
    mutates_args=(),
    device_types=["cuda"],
)
def _(
    glogp: torch.Tensor,
    R: torch.Tensor,
    L: int,
) -> torch.Tensor:
    stream = get_stream(glogp.device)
    device = wp.device_from_torch(glogp.device)
    dtype = str(glogp.dtype)

    h = torch.empty((glogp.shape[0], L),
                    device=glogp.device, dtype=glogp.dtype)
    order = R.shape[-1]

    glogp_wp = wp.from_torch(glogp.detach(), return_ctype=True)
    R_wp = wp.from_torch(R.detach(), return_ctype=True)
    h_wp = wp.from_torch(h.detach(), return_ctype=True)

    try:
        fwd_kernel = get_warp_module(f"implicit_filter_{order}_fwd", [dtype])
    except ValueError:
        fwd_kernel, bwd_kernel = generate_implicit_filter_kernels(order, dtype)
        fwd_kernel = add_warp_module(
            f"implicit_filter_{order}_fwd", [dtype], fwd_kernel)
        bwd_kernel = add_warp_module(
            f"implicit_filter_bwd", [dtype], bwd_kernel)

    wp.launch_tiled(fwd_kernel, dim=(glogp.shape[0], (L+256*4-1)//(256*4)), inputs=(
        glogp_wp, R_wp, h_wp, L), device=device, stream=stream, block_dim=256)

    return h


@torch.library.register_fake(
    "subquadratic_ops_torch::implicit_filter_fwd_primitive"
)
def _(
    glogp: torch.Tensor,
    R: torch.Tensor,
    L: int,
) -> torch.Tensor:
    order = R.shape[-1]
    h = torch.empty((glogp.shape[0], L),
                    device=glogp.device, dtype=glogp.dtype)
    return h


@torch.library.custom_op(
    "subquadratic_ops_torch::implicit_filter_bwd_primitive",
    mutates_args=(),
    device_types=["cuda"],
)
def _(
    grad_output: torch.Tensor,
    glogp: torch.Tensor,
    R: torch.Tensor,
    L: int,
) -> List[torch.Tensor]:
    stream = get_stream(glogp.device)
    device = wp.device_from_torch(glogp.device)
    dtype = str(glogp.dtype)
    d_model = glogp.shape[0]
    order = R.shape[-1]
    dlogp = torch.zeros(
        (d_model, order), device=glogp.device, dtype=glogp.dtype)
    dR = torch.zeros((d_model, order), device=glogp.device, dtype=glogp.dtype)

    glogp_wp = wp.from_torch(glogp.detach(), return_ctype=True)
    R_wp = wp.from_torch(R.detach(), return_ctype=True)
    dlogp_wp = wp.from_torch(dlogp.detach(), return_ctype=True)
    dR_wp = wp.from_torch(dR.detach(), return_ctype=True)
    grad_output_wp = wp.from_torch(grad_output.detach(), return_ctype=True)

    try:
        bwd_kernel = get_warp_module(f"implicit_filter_bwd", [dtype])
    except:
        raise ValueError(
            f"Implicit filter bwd kernel not found for dtype: {dtype}")
    wp.launch(bwd_kernel,
              dim=((L+IMPLICIT_FILTER_L_SEG_SIZE-1) //
                   IMPLICIT_FILTER_L_SEG_SIZE, d_model, order),
              inputs=(glogp_wp, R_wp, grad_output_wp, dlogp_wp, dR_wp, L),
              device=device, stream=stream)

    return [dlogp, dR]


@torch.library.register_fake(
    "subquadratic_ops_torch::implicit_filter_bwd_primitive"
)
def _(
    grad_output: torch.Tensor,
    glogp: torch.Tensor,
    R: torch.Tensor,
    L: int,
) -> List[torch.Tensor]:
    order = R.shape[-1]
    dlogp = torch.empty((glogp.shape[0], order),
                        device=glogp.device, dtype=glogp.dtype)
    dR = torch.empty((glogp.shape[0], order),
                     device=glogp.device, dtype=glogp.dtype)

    return [dlogp, dR]


def implicit_filter_setup_fwd_context(ctx, inputs, output):
    glogp, R, L = inputs
    ctx.save_for_backward(glogp, R)
    ctx.L = L


@torch.compiler.allow_in_graph
def implicit_filter_fwd(*args):
    return torch.ops.subquadratic_ops_torch.implicit_filter_fwd_primitive(*args)


@torch.compiler.allow_in_graph
def implicit_filter_bwd(ctx, grad_outputs):

    (glogp, R) = ctx.saved_tensors
    L = ctx.L
    grad_output = grad_outputs
    results = torch.ops.subquadratic_ops_torch.implicit_filter_bwd_primitive(
        grad_output, glogp, R, L)

    dglogp, dR = results

    return dglogp, dR, None


torch.library.register_autograd(
    "subquadratic_ops_torch::implicit_filter_fwd_primitive",
    implicit_filter_bwd,
    setup_context=implicit_filter_setup_fwd_context,
)


def implicit_filter(glogp, R, L):

    if glogp.shape[-1] != R.shape[-1] or glogp.shape[0] != R.shape[0] or glogp.ndim != 2 or R.ndim != 2:
        raise ValueError(
            f"glogp and R must have the same order and d_model, got {glogp.shape[-1]} and {R.shape[-1]} and {glogp.shape[0]} and {R.shape[0]} and {glogp.ndim} and {R.ndim}")

    return implicit_filter_fwd(glogp, R, L)
