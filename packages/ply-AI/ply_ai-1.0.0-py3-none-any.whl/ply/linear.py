import torch
import torch.nn as nn
import triton
import triton.language as tl

# ==========================================
# 0. 硬件感知大脑
# ==========================================
def get_adaptive_config():
    if not torch.cuda.is_available(): return []
    props = torch.cuda.get_device_properties(0)
    cc = props.major
    sm_count = props.multi_processor_count
    
    # 基础配置
    configs = [
        triton.Config({'BLOCK_M': 128, 'BLOCK_N': 128, 'BLOCK_K': 32, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
        triton.Config({'BLOCK_M': 64,  'BLOCK_N': 128, 'BLOCK_K': 32, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
    ]

    # 高端卡 (5090/4090)
    if cc >= 9 or (cc == 8 and sm_count > 80):
        configs += [
            triton.Config({'BLOCK_M': 128, 'BLOCK_N': 256, 'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=3, num_warps=8),
            triton.Config({'BLOCK_M': 256, 'BLOCK_N': 128, 'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=3, num_warps=8),
            triton.Config({'BLOCK_M': 64,  'BLOCK_N': 256, 'BLOCK_K': 32, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
            triton.Config({'BLOCK_M': 128, 'BLOCK_N': 64,  'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=4, num_warps=4),
        ]
    # 中端卡 (3060 等)
    else:
        configs += [
            triton.Config({'BLOCK_M': 64, 'BLOCK_N': 64, 'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
            triton.Config({'BLOCK_M': 32, 'BLOCK_N': 64, 'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=4),
            triton.Config({'BLOCK_M': 64, 'BLOCK_N': 32, 'BLOCK_K': 64, 'GROUP_SIZE_M': 8}, num_stages=2, num_warps=2),
        ]
    return configs

DYNAMIC_CONFIGS = get_adaptive_config()

# ==========================================
# 1. MatMul Kernel
# ==========================================
@triton.autotune(configs=DYNAMIC_CONFIGS, key=['M', 'N', 'K'])
@triton.jit
def matmul_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
    GROUP_SIZE_M: tl.constexpr, ACTIVATION: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_n = (pid % num_pid_in_group) // group_size_m

    offs_am = (pid_m * BLOCK_M + tl.arange(0, BLOCK_M)) % M
    offs_bn = (pid_n * BLOCK_N + tl.arange(0, BLOCK_N)) % N
    offs_k = tl.arange(0, BLOCK_K)
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)
    b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn)

    accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k in range(0, tl.cdiv(K, BLOCK_K)):
        a = tl.load(a_ptrs, mask=offs_k[None, :] < K - k * BLOCK_K, other=0.0)
        b = tl.load(b_ptrs, mask=offs_k[:, None] < K - k * BLOCK_K, other=0.0)
        accumulator += tl.dot(a, b)
        a_ptrs += BLOCK_K * stride_ak
        b_ptrs += BLOCK_K * stride_bk
    
    if ACTIVATION == 1: accumulator = tl.maximum(accumulator, 0.0)
    elif ACTIVATION == 3: accumulator = accumulator * tl.sigmoid(accumulator)
    
    c = accumulator.to(tl.float16)
    offs_cm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_cn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    c_ptrs = c_ptr + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]
    c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)
    tl.store(c_ptrs, c, mask=c_mask)

# ==========================================
# 2. Gradient W Kernel
# ==========================================
@triton.autotune(configs=DYNAMIC_CONFIGS, key=['M', 'N', 'K'])
@triton.jit
def matmul_grad_w_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_am, stride_ak, stride_bk, stride_bn, stride_cm, stride_cn,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
    GROUP_SIZE_M: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    num_pid_in_group = GROUP_SIZE_M * num_pid_n
    group_id = pid // num_pid_in_group
    first_pid_m = group_id * GROUP_SIZE_M
    group_size_m = min(num_pid_m - first_pid_m, GROUP_SIZE_M)
    pid_m = first_pid_m + (pid % group_size_m)
    pid_n = (pid % num_pid_in_group) // group_size_m

    offs_am = (pid_m * BLOCK_M + tl.arange(0, BLOCK_M)) % M
    offs_bn = (pid_n * BLOCK_N + tl.arange(0, BLOCK_N)) % N
    offs_k = tl.arange(0, BLOCK_K)
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)
    b_ptrs = b_ptr + (offs_k[:, None] * stride_bk + offs_bn[None, :] * stride_bn)

    accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    for k in range(0, tl.cdiv(K, BLOCK_K)):
        a = tl.load(a_ptrs, mask=offs_k[None, :] < K - k * BLOCK_K, other=0.0)
        b = tl.load(b_ptrs, mask=offs_k[:, None] < K - k * BLOCK_K, other=0.0)
        accumulator += tl.dot(a, b)
        a_ptrs += BLOCK_K * stride_ak
        b_ptrs += BLOCK_K * stride_bk
        
    c = accumulator.to(tl.float16)
    offs_cm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_cn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    c_ptrs = c_ptr + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]
    c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)
    tl.store(c_ptrs, c, mask=c_mask)

# ==========================================
# 3. Bias Grad Kernel
# ==========================================
@triton.jit
def bias_grad_kernel(dY_ptr, dB_ptr, M, N, stride_dym, stride_dyn, BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr):
    pid_n = tl.program_id(0)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    acc = tl.zeros([BLOCK_N], dtype=tl.float32)
    for start_m in range(0, M, BLOCK_M):
        offs_m = start_m + tl.arange(0, BLOCK_M)
        mask = (offs_m[:, None] < M) & (offs_n[None, :] < N)
        val = tl.load(dY_ptr + offs_m[:, None] * stride_dym + offs_n[None, :] * stride_dyn, mask=mask, other=0.0)
        acc += tl.sum(val, axis=0)
    tl.store(dB_ptr + offs_n, acc.to(tl.float16), mask=offs_n < N)

# ==========================================
# 4. Autograd & Wrapper (FIXED)
# ==========================================
class PlyLinearFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, input, weight, bias=None, activation_id=0):
        ctx.save_for_backward(input, weight, bias)
        ctx.activation_id = activation_id
        M, K = input.shape
        N, K_w = weight.shape
        y = torch.empty((M, N), device=input.device, dtype=input.dtype)
        grid = lambda META: (triton.cdiv(M, META['BLOCK_M']) * triton.cdiv(N, META['BLOCK_N']), )
        
        # [FIX] 移除了显式的 GROUP_SIZE_M=8，由 Autotuner 控制
        matmul_kernel[grid](
            input, weight, y, M, N, K,
            input.stride(0), input.stride(1), weight.stride(1), weight.stride(0), y.stride(0), y.stride(1),
            ACTIVATION=activation_id
        )
        if bias is not None: y += bias
        return y

    @staticmethod
    def backward(ctx, grad_output):
        input, weight, bias = ctx.saved_tensors
        M, N = grad_output.shape
        N, K = weight.shape
        grad_input = grad_weight = grad_bias = None
        
        if ctx.needs_input_grad[0]: # dX
            grad_input = torch.empty_like(input)
            grid = lambda META: (triton.cdiv(M, META['BLOCK_M']) * triton.cdiv(K, META['BLOCK_N']), )
            # [FIX] 移除 GROUP_SIZE_M
            matmul_kernel[grid](
                grad_output, weight, grad_input, M, K, N,
                grad_output.stride(0), grad_output.stride(1), weight.stride(0), weight.stride(1),
                grad_input.stride(0), grad_input.stride(1),
                ACTIVATION=0
            )
        
        if ctx.needs_input_grad[1]: # dW
            grad_weight = torch.empty((N, K), device=weight.device, dtype=weight.dtype)
            grid = lambda META: (triton.cdiv(N, META['BLOCK_M']) * triton.cdiv(K, META['BLOCK_N']), )
            # [FIX] 移除 GROUP_SIZE_M
            matmul_grad_w_kernel[grid](
                grad_output, input, grad_weight, N, K, M,
                grad_output.stride(1), grad_output.stride(0), input.stride(0), input.stride(1),
                grad_weight.stride(0), grad_weight.stride(1)
            )
            
        if bias is not None and ctx.needs_input_grad[2]: # dB
            grad_bias = torch.empty((N,), device=weight.device, dtype=weight.dtype)
            bias_grad_kernel[(triton.cdiv(N, 64),)](
                grad_output, grad_bias, M, N,
                grad_output.stride(0), grad_output.stride(1), BLOCK_M=128, BLOCK_N=64
            )
        return grad_input, grad_weight, grad_bias, None

class PlyLinear(nn.Module):
    def __init__(self, in_features, out_features, bias=True, activation=None):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.weight = nn.Parameter(torch.randn(out_features, in_features))
        self.bias = nn.Parameter(torch.zeros(out_features)) if bias else None
        nn.init.kaiming_uniform_(self.weight, a=5**0.5)
        if self.bias is not None: nn.init.uniform_(self.bias, -0.1, 0.1)
        self.act_id = 0
        if activation == 'relu': self.act_id = 1
        elif activation == 'silu': self.act_id = 3
        
        if not hasattr(self, '_logged'):
            self._logged = True

    def forward(self, x):
        is_3d = x.dim() == 3
        if is_3d: B, S, D = x.shape; x = x.view(-1, D)
        y = PlyLinearFunction.apply(x, self.weight, self.bias, self.act_id)
        if is_3d: y = y.view(B, S, -1)
        return y
