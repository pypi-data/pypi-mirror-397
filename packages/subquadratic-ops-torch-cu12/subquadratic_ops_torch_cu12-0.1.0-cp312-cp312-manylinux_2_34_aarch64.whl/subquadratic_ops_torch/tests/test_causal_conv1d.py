# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: LicenseRef-NvidiaProprietary
#
# NVIDIA CORPORATION, its affiliates and licensors retain all intellectual
# property and proprietary rights in and to this material, related
# documentation and any modifications thereto. Any use, reproduction,
# disclosure or distribution of this material and related documentation
# without an express license agreement from NVIDIA CORPORATION or
# its affiliates is strictly prohibited.

import pytest

import torch
from utils import Conv1DModel

from subquadratic_ops_torch.causal_conv1d import causal_conv1d

torch.backends.cuda.matmul.allow_tf32 = False
torch.backends.cudnn.allow_tf32 = False


torch.manual_seed(9)

dtype_fp64 = torch.float64
dtype_fp32 = torch.float32
dtype_bf16 = torch.bfloat16


@pytest.mark.parametrize("dtype", [dtype_fp64])
@pytest.mark.parametrize("in_dim", [1024, 4096])
@pytest.mark.parametrize("seq_dim", [8192, 510])
@pytest.mark.parametrize("conv_width", [3, 4])
def test_causal_conv1d(in_dim, seq_dim, conv_width, dtype):
    model = Conv1DModel(in_dim, conv_width, dtype).cuda()
    batch_size = 2

    x = torch.randn(batch_size, in_dim, seq_dim).cuda().to(dtype_bf16)
    weights = torch.randn(in_dim, conv_width).cuda().to(dtype_bf16)
    model.conv.weight.data = weights.reshape(in_dim, 1, conv_width).to(dtype)
    model.weight.data = weights.to(dtype)

    y_predicted = causal_conv1d(x.to(dtype), weights.to(dtype))
    y_actual = model(x.to(dtype))

    torch.testing.assert_close(y_predicted.to(
        dtype), y_actual.to(dtype), atol=1e-6, rtol=1e-6)


@pytest.mark.parametrize("dtype", [dtype_fp64])
@pytest.mark.parametrize("in_dim", [4, 1])
@pytest.mark.parametrize("seq_dim", [8, 2])
@pytest.mark.parametrize("conv_width", [3, 2])
def test_causal_conv1d_bwd(in_dim, seq_dim, conv_width, dtype):
    batch_size = 2

    x = torch.randn(batch_size, in_dim, seq_dim).cuda().to(dtype_bf16)
    weights = torch.randn(in_dim, conv_width).cuda().to(dtype_bf16)

    x.requires_grad = True
    weights.requires_grad = True

    torch.autograd.gradcheck(causal_conv1d, (x.to(dtype), weights.to(dtype)))
