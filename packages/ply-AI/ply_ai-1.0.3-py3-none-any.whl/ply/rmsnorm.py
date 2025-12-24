import torch
import triton
import triton.language as tl

# ==========================================
# 核心引擎: RMSNorm Kernel
# ==========================================
# 优化点：
# 1. 显存读写最小化：只读一次 x，只写一次 y。
# 2. 寄存器计算：平方、求和、开根号都在 SRAM 里完成。
@triton.jit
def rmsnorm_kernel(
    x_ptr,      # 输入数据指针
    w_ptr,      # 权重指针 (gamma)
    out_ptr,    # 输出指针
    stride_x_row, # 输入每行的 stride
    stride_w,     # 权重的 stride
    stride_out_row, # 输出每行的 stride
    N_COLS,       # 列数 (Hidden Size)
    eps,          # 防止除零
    BLOCK_SIZE: tl.constexpr # 块大小 (需 >= N_COLS)
):
    # 1. 确定当前处理哪一行
    row_idx = tl.program_id(0)
    
    # 2. 准备指针
    row_start_ptr = x_ptr + row_idx * stride_x_row
    offsets = tl.arange(0, BLOCK_SIZE)
    mask = offsets < N_COLS

    # 3. 加载数据 (Load)
    # 关键：FP16 输入 -> 转 FP32 计算 (保证精度)
    x = tl.load(row_start_ptr + offsets, mask=mask, other=0.0).to(tl.float32)
    w = tl.load(w_ptr + offsets * stride_w, mask=mask, other=0.0).to(tl.float32)

    # 4. 计算 RMS (均方根)
    # PyTorch 需要三步: x^2 -> mean -> rsqrt，这里一步到位
    x_sq = x * x
    mean_sq = tl.sum(x_sq, axis=0) / N_COLS
    rsqrt = tl.rsqrt(mean_sq + eps)

    # 5. 归一化 & 缩放
    out = x * rsqrt * w

    # 6. 写回 (Store)
    # 转回 FP16 写回显存
    out_row_start_ptr = out_ptr + row_idx * stride_out_row
    tl.store(out_row_start_ptr + offsets, out.to(tl.float16), mask=mask)

# ==========================================
# 封装层：PlyRMSNorm
# ==========================================
class PlyRMSNorm(torch.nn.Module):
    def __init__(self, hidden_size, eps=1e-6):
        super().__init__()
        self.weight = torch.nn.Parameter(torch.ones(hidden_size))
        self.eps = eps

    def forward(self, x):
        # 展平为 [Total_Rows, Hidden_Size]
        orig_shape = x.shape
        N = x.shape[-1]
        M = x.numel() // N
        
        x_flat = x.view(M, N)
        y_flat = torch.empty_like(x_flat)
        
        # 自动计算 Block Size (必须是 2 的幂次)
        BLOCK_SIZE = triton.next_power_of_2(N)
        
        # Grid: 一行对应一个 Block
        grid = (M, )
        
        rmsnorm_kernel[grid](
            x_flat, self.weight, y_flat,
            x_flat.stride(0),
            self.weight.stride(0),
            y_flat.stride(0),
            N, self.eps,
            BLOCK_SIZE=BLOCK_SIZE
        )
        
        return y_flat.view(*orig_shape)

# ==========================================
# 极限跑分测试
# ==========================================
if __name__ == "__main__":
    torch.manual_seed(0)
    
    # 模拟 LLaMA-2-7B 的负载
    BATCH_TOKENS = 16 * 1024 
    HIDDEN_SIZE = 4096
    
    print(f"🚀 Benchmarking RMSNorm (Memory Bound Operator)...")
    print(f"    Input: [{BATCH_TOKENS}, {HIDDEN_SIZE}] (FP16)")
    print(f"    Hardware: NVIDIA RTX 4090")
    
    if not torch.cuda.is_available():
        print("❌ No GPU found")
        exit(1)
    
    # 准备数据
    x = torch.randn(BATCH_TOKENS, HIDDEN_SIZE, device='cuda', dtype=torch.float16)
    
    # 1. Ply 实现
    ply_norm = PlyRMSNorm(HIDDEN_SIZE).cuda()
    
    # 2. PyTorch 原生实现
    class TorchRMSNorm(torch.nn.Module):
        def __init__(self, dim, eps=1e-6):
            super().__init__()
            self.eps = eps
            self.weight = torch.nn.Parameter(torch.ones(dim))
        def forward(self, x):
            dtype = x.dtype
            x = x.float() # 强制 FP32 计算
            variance = x.pow(2).mean(-1, keepdim=True)
            x = x * torch.rsqrt(variance + self.eps)
            # [FIXED] 确保 weight 也是 float 参与计算，最后再转回 FP16
            return (self.weight.float() * x).to(dtype)

    # [FIXED] 加上 .half() 确保权重是 FP16，虽然 forward 里转了 float，但验证时类型要对齐
    torch_norm = TorchRMSNorm(HIDDEN_SIZE).cuda().half()
    
    # --- 1. 验证正确性 ---
    print("🔍 Validating...")
    ply_out = ply_norm(x)
    torch_out = torch_norm(x)
    
    # RMSNorm 涉及累加，FP16下误差会比 MatMul 大一点点，是正常的
    if torch.allclose(ply_out, torch_out, atol=1e-2, rtol=1e-2):
        print("✅ Correctness: PASSED")
    else:
        print("⚠️ Mismatch")
        print(f"   Max Diff: {(ply_out - torch_out).abs().max().item()}")

    # --- 2. 性能测试 ---
    print("⏱️  Speed Test...")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    # PyTorch
    for _ in range(10): _ = torch_norm(x) # 预热
    start.record()
    for _ in range(200): # 跑 200 轮
        _ = torch_norm(x)
    end.record()
    torch.cuda.synchronize()
    torch_ms = start.elapsed_time(end) / 200
    
    # Ply
    for _ in range(10): _ = ply_norm(x) # 预热
    start.record()
    for _ in range(200):
        _ = ply_norm(x)
    end.record()
    torch.cuda.synchronize()
    ply_ms = start.elapsed_time(end) / 200
    
    print("-" * 60)
    print(f"PyTorch RMSNorm: {torch_ms:.4f} ms")
    print(f"Ply RMSNorm:     {ply_ms:.4f} ms")
    print(f"⚡ Speedup: {torch_ms/ply_ms:.2f}x")
    
    # 有效显存带宽
    total_bytes = 4 * x.numel() # Read X(2) + Write Y(2)
    gb_s = (total_bytes / 1e9) / (ply_ms / 1000)
    print(f"💾 Effective Bandwidth: {gb_s:.2f} GB/s")
    print("-" * 60)

