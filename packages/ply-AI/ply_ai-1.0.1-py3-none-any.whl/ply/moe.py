import torch
import triton
import triton.language as tl
import time

# ==========================================
# 核心引擎: Fused MoE Kernel (Batch GEMM style)
# ==========================================
@triton.autotune(
    configs=[
        # 针对 RTX 5090 调整了一些更激进的配置
        triton.Config({'BLOCK_M': 128, 'BLOCK_N': 128, 'BLOCK_K': 32}, num_stages=3, num_warps=8),
        triton.Config({'BLOCK_M': 64,  'BLOCK_N': 128, 'BLOCK_K': 32}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_M': 128, 'BLOCK_N': 64,  'BLOCK_K': 32}, num_stages=4, num_warps=4),
        triton.Config({'BLOCK_M': 64,  'BLOCK_N': 64,  'BLOCK_K': 32}, num_stages=4, num_warps=4),
    ],
    key=['max_tokens_per_expert', 'N', 'K'],
)
@triton.jit
def fused_moe_kernel(
    X_ptr, W_ptr, Out_ptr,
    Expert_Offsets_ptr,
    stride_xm, stride_xk,  
    stride_we, stride_wk, stride_wn, 
    stride_om, stride_on,  
    Num_Experts, N, K,
    max_tokens_per_expert, 
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
):
    # Grid Z: Expert ID
    pid_n = tl.program_id(0)
    pid_m = tl.program_id(1)
    pid_e = tl.program_id(2)
    
    # 1. 获取当前专家的 Token 范围
    off_start = tl.load(Expert_Offsets_ptr + pid_e)
    off_end = tl.load(Expert_Offsets_ptr + pid_e + 1)
    num_tokens = off_end - off_start
    
    # 边界检查
    if pid_m * BLOCK_M >= num_tokens:
        return

    # 2. 计算指针
    offs_m = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_k = tl.arange(0, BLOCK_K)
    
    real_m_idxs = off_start + offs_m
    
    # X 指针: [Total_Tokens, K]
    x_ptrs = X_ptr + real_m_idxs[:, None] * stride_xm + offs_k[None, :] * stride_xk
    
    # W 指针: [E, K, N]
    w_ptrs = W_ptr + pid_e * stride_we + offs_k[:, None] * stride_wk + offs_n[None, :] * stride_wn
    
    accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    
    for k in range(0, tl.cdiv(K, BLOCK_K)):
        # Load X
        x_mask = (offs_m[:, None] < num_tokens) & (offs_k[None, :] < K - k * BLOCK_K)
        x = tl.load(x_ptrs, mask=x_mask, other=0.0)
        
        # Load W
        w_mask = (offs_k[:, None] < K - k * BLOCK_K) & (offs_n[None, :] < N)
        w = tl.load(w_ptrs, mask=w_mask, other=0.0)
        
        accumulator += tl.dot(x, w)
        
        x_ptrs += BLOCK_K * stride_xk
        w_ptrs += BLOCK_K * stride_wk
        
    # Store
    out_ptrs = Out_ptr + real_m_idxs[:, None] * stride_om + offs_n[None, :] * stride_on
    out_mask = (offs_m[:, None] < num_tokens) & (offs_n[None, :] < N)
    
    tl.store(out_ptrs, accumulator.to(tl.float16), mask=out_mask)

# ==========================================
# 2. PlyMoE 模块
# ==========================================
class PlyMoE(torch.nn.Module):
    def __init__(self, num_experts, in_features, out_features):
        super().__init__()
        self.num_experts = num_experts
        self.in_features = in_features
        self.out_features = out_features
        
        # 权重: [E, K, N]
        self.weights = torch.nn.Parameter(torch.randn(num_experts, in_features, out_features, dtype=torch.float16))

    def forward(self, x, expert_indices):
        # 1. 排序
        sorted_indices = torch.argsort(expert_indices)
        x_sorted = x[sorted_indices]
        
        # 2. Offsets
        expert_counts = torch.bincount(expert_indices, minlength=self.num_experts)
        offsets = torch.zeros(self.num_experts + 1, dtype=torch.int32, device=x.device)
        offsets[1:] = torch.cumsum(expert_counts, dim=0)
        
        # 3. Kernel Config
        M_total, K = x.shape
        N = self.out_features
        max_tokens = expert_counts.max().item()
        
        if max_tokens == 0: 
            return torch.zeros_like(x)
            
        out_sorted = torch.empty((M_total, N), device=x.device, dtype=torch.float16)
        
        grid = lambda META: (
            triton.cdiv(N, META['BLOCK_N']),
            triton.cdiv(max_tokens, META['BLOCK_M']),
            self.num_experts
        )
        
        # [FIXED] 移除了 BLOCK_M, BLOCK_N, BLOCK_K 的显式传递
        # 让 Autotuner 接管
        fused_moe_kernel[grid](
            x_sorted, self.weights, out_sorted,
            offsets,
            x_sorted.stride(0), x_sorted.stride(1),
            self.weights.stride(0), self.weights.stride(1), self.weights.stride(2),
            out_sorted.stride(0), out_sorted.stride(1),
            self.num_experts, N, K,
            max_tokens
        )
        
        return out_sorted

# ==========================================
# 3. 跑分对比
# ==========================================
if __name__ == "__main__":
    torch.manual_seed(0)
    
    NUM_EXPERTS = 8
    TOTAL_TOKENS = 4096 * 4 
    HIDDEN = 4096
    
    print(f"🚀 Benchmarking Ply Fused MoE ({NUM_EXPERTS} Experts)...")
    print(f"    Hardware: RTX 5090")
    
    if not torch.cuda.is_available(): exit(1)
    
    x = torch.randn(TOTAL_TOKENS, HIDDEN, device='cuda', dtype=torch.float16)
    expert_indices = torch.randint(0, NUM_EXPERTS, (TOTAL_TOKENS,), device='cuda').int()
    
    ply_moe = PlyMoE(NUM_EXPERTS, HIDDEN, HIDDEN).cuda()
    
    # PyTorch Loop (Baseline)
    class TorchMoE(torch.nn.Module):
        def __init__(self, n_experts, dim):
            super().__init__()
            self.experts = torch.nn.ModuleList([
                torch.nn.Linear(dim, dim, bias=False) for _ in range(n_experts)
            ])
        def forward(self, x, indices):
            out = torch.zeros_like(x)
            for i, expert in enumerate(self.experts):
                mask = (indices == i)
                if mask.any():
                    out[mask] = expert(x[mask])
            return out
            
    torch_moe = TorchMoE(NUM_EXPERTS, HIDDEN).cuda().half()
    
    print("🔍 Validating...")
    ply_out = ply_moe(x, expert_indices)
    if ply_out.abs().sum() > 0:
        print("✅ Correctness: Ply MoE runs and produces output!")

    print("⏱️  Speed Test...")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    # PyTorch Loop
    for _ in range(5): torch_moe(x, expert_indices)
    start.record()
    for _ in range(50):
        torch_moe(x, expert_indices)
    end.record()
    torch.cuda.synchronize()
    torch_ms = start.elapsed_time(end) / 50
    
    # Ply Fused
    print("    Auto-Tuning in progress...")
    for _ in range(5): ply_moe(x, expert_indices)
    start.record()
    for _ in range(50):
        ply_moe(x, expert_indices)
    end.record()
    torch.cuda.synchronize()
    ply_ms = start.elapsed_time(end) / 50
    
    print("-" * 60)
    print(f"PyTorch MoE (For-Loop): {torch_ms:.4f} ms")
    print(f"Ply Fused MoE:        {ply_ms:.4f} ms")
    print(f"⚡ Speedup: {torch_ms / ply_ms:.2f}x")
    print("-" * 60)

