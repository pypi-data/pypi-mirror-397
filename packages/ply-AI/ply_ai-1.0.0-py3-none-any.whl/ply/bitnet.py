import torch
import triton
import triton.language as tl

# ==========================================
# 0. 辅助工具: 2-bit 打包逻辑 (Python端)
# ==========================================
# 映射规则: 0->00, +1->01, -1->10
def pack_ternary_weights(w):
    # w: [-1, 0, 1] 的 float/int 张量
    assert w.dim() == 2
    N, K = w.shape
    assert K % 4 == 0, "Hidden dim must be divisible by 4"
    
    # 映射
    w_mapped = torch.zeros_like(w, dtype=torch.uint8)
    w_mapped[w == 1] = 1
    w_mapped[w == -1] = 2
    
    # Pack
    w_packed = torch.zeros((N, K // 4), dtype=torch.uint8, device=w.device)
    w_packed |= (w_mapped[:, 0::4] << 0)
    w_packed |= (w_mapped[:, 1::4] << 2)
    w_packed |= (w_mapped[:, 2::4] << 4)
    w_packed |= (w_mapped[:, 3::4] << 6)
    
    return w_packed

# ==========================================
# 1. BitNet Kernel (2-bit 解包 + MatMul)
# ==========================================
@triton.jit
def bitnet_matmul_kernel(
    a_ptr, b_ptr, c_ptr,
    M, N, K,
    stride_am, stride_ak,
    stride_bk, stride_bn,
    stride_cm, stride_cn,
    BLOCK_M: tl.constexpr, BLOCK_N: tl.constexpr, BLOCK_K: tl.constexpr,
):
    pid = tl.program_id(axis=0)
    num_pid_m = tl.cdiv(M, BLOCK_M)
    num_pid_n = tl.cdiv(N, BLOCK_N)
    pid_m = pid % num_pid_m
    pid_n = pid // num_pid_m

    offs_am = (pid_m * BLOCK_M + tl.arange(0, BLOCK_M)) % M
    offs_bn = (pid_n * BLOCK_N + tl.arange(0, BLOCK_N)) % N
    offs_k = tl.arange(0, BLOCK_K)
    
    # 计算 A 的指针
    a_ptrs = a_ptr + (offs_am[:, None] * stride_am + offs_k[None, :] * stride_ak)
    
    # 计算 B 的指针 (注意 B 是压缩过的)
    # 我们将在 loop 内部动态计算 offsets，这里先不初始化 b_ptrs
    
    accumulator = tl.zeros((BLOCK_M, BLOCK_N), dtype=tl.float32)
    
    for k in range(0, tl.cdiv(K, BLOCK_K)):
        # --- Load A ---
        # 边界检查: k维度是否越界
        k_remaining = K - k * BLOCK_K
        a_mask = offs_k[None, :] < k_remaining
        
        a = tl.load(a_ptrs, mask=a_mask, other=0.0)
        
        # --- Load B (Packed) ---
        # 1. 计算当前块在 K 维度的绝对坐标
        current_k_start = k * BLOCK_K
        
        # 2. 计算压缩后的索引 (除以 4)
        # offs_k 是 [0, 1, ... BLOCK_K-1]
        # packed_k_idxs 将会是 [0, 0, 0, 0, 1, 1, 1, 1 ...]
        # 这意味着我们同一个 byte 会读取 4 次，这是 Triton 向量化加载的特性
        # 虽然有点浪费带宽，但逻辑简单且利用了 L1 Cache
        packed_k_idxs = (current_k_start + offs_k) // 4
        
        # 3. 计算位移量
        shift_amounts = ((current_k_start + offs_k) % 4) * 2
        
        # 4. 计算 B 的指针地址
        # B shape [K/4, N]
        # offs_k 是行(K)，offs_bn 是列(N)
        b_ptrs_curr = b_ptr + packed_k_idxs[:, None] * stride_bk + offs_bn[None, :] * stride_bn
        
        # [FIXED] 添加 Mask
        # 我们需要检查 K 边界 (虽然是压缩的，但逻辑 K 索引必须在范围内)
        # 同时也检查 N 边界
        b_mask = (offs_k[:, None] < k_remaining) & (offs_bn[None, :] < N)
        
        b_packed = tl.load(b_ptrs_curr, mask=b_mask, other=0)
        
        # --- Unpack (On-the-fly) ---
        # (byte >> shift) & 0x3
        b_2bit = (b_packed >> shift_amounts[:, None]) & 0x3
        
        # Map 0->0, 1->1, 2->-1
        # 这是一个无分支的转换
        b_fp16 = (b_2bit == 1).to(tl.float16) - (b_2bit == 2).to(tl.float16)
        
        # --- Compute ---
        accumulator += tl.dot(a, b_fp16)
        
        # 步进 A
        a_ptrs += BLOCK_K * stride_ak
        
    c = accumulator.to(tl.float16)
    offs_cm = pid_m * BLOCK_M + tl.arange(0, BLOCK_M)
    offs_cn = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    c_ptrs = c_ptr + stride_cm * offs_cm[:, None] + stride_cn * offs_cn[None, :]
    c_mask = (offs_cm[:, None] < M) & (offs_cn[None, :] < N)
    tl.store(c_ptrs, c, mask=c_mask)

# ==========================================
# 2. PlyBitLinear 模块
# ==========================================
class PlyBitLinear(torch.nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        
        # 随机生成 [-1, 0, 1] 权重
        raw_w = torch.randint(-1, 2, (out_features, in_features), dtype=torch.float32)
        
        # 打包 (Pack) -> (K/4, N)
        # 注意: Triton Kernel 期望 B 是 (K, N) 布局 (Col-Major conceptually for weights often)
        # 这里我们按 (In, Out) 即 (K, N) 存储
        w_t = raw_w.t().contiguous()
        self.register_buffer('packed_weight', pack_ternary_weights(w_t))
        
        self.scale = torch.nn.Parameter(torch.tensor(1.0 / (in_features ** 0.5)))

    def forward(self, x):
        M, K = x.shape
        N = self.out_features
        
        y = torch.empty((M, N), device=x.device, dtype=torch.float16)
        
        grid = lambda META: (
            triton.cdiv(M, META['BLOCK_M']) * triton.cdiv(N, META['BLOCK_N']),
        )
        
        bitnet_matmul_kernel[grid](
            x, self.packed_weight, y,
            M, N, K,
            x.stride(0), x.stride(1),
            self.packed_weight.stride(0), self.packed_weight.stride(1),
            y.stride(0), y.stride(1),
            BLOCK_M=128, BLOCK_N=128, BLOCK_K=64 # 稍微加大 K 块大小以利用带宽
        )
        
        return y * self.scale

# ==========================================
# 3. 验证与对比
# ==========================================
if __name__ == "__main__":
    torch.manual_seed(0)
    
    M = 4096 
    K = 4096 
    N = 4096 
    
    print(f"🚀 Benchmarking Ply-BitLinear (1.58-bit / 2-bit Packed)...")
    print(f"    Shape: {M}x{K} @ {K}x{N}")
    
    if not torch.cuda.is_available(): exit(1)
    
    x = torch.randn(M, K, device='cuda', dtype=torch.float16)
    bit_layer = PlyBitLinear(K, N).cuda()
    
    # 显存对比
    print("-" * 40)
    print(f"    FP16 Weight Size:   {2 * K * N / 1024**2:.2f} MB")
    print(f"    BitNet Weight Size: {bit_layer.packed_weight.numel() / 1024**2:.2f} MB (⬇️ 87.5% reduction!)")
    print("-" * 40)
    
    print("⏱️  Speed Test...")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    # Ply BitNet
    for _ in range(10): bit_layer(x)
    start.record()
    for _ in range(100):
        bit_layer(x)
    end.record()
    torch.cuda.synchronize()
    ply_ms = start.elapsed_time(end) / 100
    
    # PyTorch FP16
    torch_layer = torch.nn.Linear(K, N, bias=False).cuda().half()
    for _ in range(10): torch_layer(x)
    start.record()
    for _ in range(100):
        torch_layer(x)
    end.record()
    torch.cuda.synchronize()
    torch_ms = start.elapsed_time(end) / 100
    
    print(f"    PyTorch FP16 Linear: {torch_ms:.4f} ms")
    print(f"    Ply BitNet Linear:   {ply_ms:.4f} ms")
    print(f"    ⚡ Speedup: {torch_ms / ply_ms:.2f}x")

