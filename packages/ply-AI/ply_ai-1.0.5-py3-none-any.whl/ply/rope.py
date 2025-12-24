import torch
import triton
import triton.language as tl

# ==========================================
# 核心引擎: RoPE Kernel
# ==========================================
# 数学原理:
# 将向量 x 分为前半部分 x_1 和后半部分 x_2
# x_new_1 = x_1 * cos - x_2 * sin
# x_new_2 = x_2 * cos + x_1 * sin
@triton.jit
def rope_kernel(
    t_ptr,      # 输入张量 (Q 或 K)
    c_ptr,      # Cos 表指针
    s_ptr,      # Sin 表指针
    out_ptr,    # 输出指针
    # 步长
    stride_batch, stride_seq, stride_head, stride_dim,
    stride_c_seq, stride_c_dim, # Cos/Sin 步长
    # 形状
    SEQ_LEN, HEAD_DIM,
    # 块大小
    BLOCK_SIZE: tl.constexpr
):
    # 1. 计算索引
    # RoPE 是 Element-wise 操作，我们每个线程处理一个 Head 的一部分
    pid = tl.program_id(0)
    
    # 解析 pid 对应的 Batch, Seq, Head
    # 这里的 Grid 我们设为 (Batch * Seq * Head)
    # 我们只并行化这三个维度，DIM 维度在 Block 内部处理
    batch_seq_head_idx = pid
    
    # 2. 计算当前处理的 Head 的起始位置
    # 假设输入是 [Batch, Seq, Head, Dim] 布局
    # 为了简化，我们只计算相对于 t_ptr 的总偏移量
    # 这种写法假设我们从外部传入展平后的 Grid
    pass 
    # (由于 Triton 的 Grid 映射比较灵活，我们在 Python端计算 Offset 更简单)
    
    # 重新设计：让每个 Block 处理一行 (即一个 Head 的 Dim 维度)
    # Grid = (Total_Tokens * Num_Heads, )
    row_idx = pid 
    
    # 3. 计算 Cos/Sin 的索引 (取决于 Seq 维度)
    # 假设输入展平为 [Total_Tokens * Num_Heads, Head_Dim]
    # 我们需要知道当前是第几个 Token (Seq_Idx)
    # Num_Heads 是常数吗？为了通用性，我们通过 stride 反推
    
    # 为了性能，我们简化场景：
    # 输入已经被 reshape 成 [Total_Rows, Head_Dim]
    # 我们还需要传入一个 seq_ids 数组，告诉 Kernel每一行对应哪个位置
    # 但为了兼容 PyTorch 的 RoPE 接口，通常是传入 offset
    
    # 这里演示 LLaMA 风格的 RoPE:
    # 每一个 Block 处理 Head_Dim 的一半 (HALF_DIM)
    HALF_DIM = HEAD_DIM // 2
    
    # 偏移量 [0, 1, ... HALF_DIM-1]
    offsets = tl.arange(0, BLOCK_SIZE)
    mask = offsets < HALF_DIM

    # 计算输入指针 (前半部分 x1)
    # t_ptr 已经偏移到了当前 Head 的起始位置
    x1_ptr = t_ptr + row_idx * stride_head + offsets * stride_dim
    # 计算输入指针 (后半部分 x2)
    x2_ptr = t_ptr + row_idx * stride_head + (offsets + HALF_DIM) * stride_dim
    
    # 加载 x1, x2
    x1 = tl.load(x1_ptr, mask=mask, other=0.0).to(tl.float32)
    x2 = tl.load(x2_ptr, mask=mask, other=0.0).to(tl.float32)
    
    # 加载 cos, sin
    # 需要计算当前 row 对应的 seq_idx。
    # 假设 t_ptr 已经是 [Batch, Seq, Head, Dim]
    # row_idx = batch_idx * (Seq * Head) + seq_idx * Head + head_idx
    # 这种除法在 Kernel 里很慢。
    
    # === 极速方案 ===
    # 我们让 Python 算好 Cos/Sin 的指针传进来！
    # 假设 c_ptr, s_ptr 已经广播到了跟 t_ptr 一样的形状 [Total_Rows, Dim]
    # 或者更常见的：Cos/Sin 是 [Max_Seq, Dim]，我们需要查表
    
    # 这里采用查表法: 传入 seq_start_idx
    # 实际上，为了极致速度，我们直接计算 Cos/Sin 指针
    # 我们假设 c_ptr 指向的是当前 batch/seq 对应的 cos 行
    # 这需要 Python 端配合。这里为了 Demo 简单，我们假设 c_ptr 是 [Total_Rows, Dim] 已经展开好的
    
    c_row_ptr = c_ptr + row_idx * stride_c_seq # 这里的 stride 实际上是 Head_Dim
    s_row_ptr = s_ptr + row_idx * stride_c_seq
    
    cos = tl.load(c_row_ptr + offsets * stride_c_dim, mask=mask, other=0.0).to(tl.float32)
    sin = tl.load(s_row_ptr + offsets * stride_c_dim, mask=mask, other=0.0).to(tl.float32)
    
    # 4. 旋转计算 (Rotation)
    y1 = x1 * cos - x2 * sin
    y2 = x1 * sin + x2 * cos
    
    # 5. 写回
    out_x1_ptr = out_ptr + row_idx * stride_head + offsets * stride_dim
    out_x2_ptr = out_ptr + row_idx * stride_head + (offsets + HALF_DIM) * stride_dim
    
    tl.store(out_x1_ptr, y1.to(tl.float16), mask=mask)
    tl.store(out_x2_ptr, y2.to(tl.float16), mask=mask)

# ==========================================
# 封装层：PlyRoPE
# ==========================================
class PlyRoPE(torch.nn.Module):
    def __init__(self, head_dim, max_position_embeddings=2048, base=10000):
        super().__init__()
        self.head_dim = head_dim
        # 预计算 Cos/Sin 表 (Cache)
        inv_freq = 1.0 / (base ** (torch.arange(0, head_dim, 2).float() / head_dim))
        t = torch.arange(max_position_embeddings).float()
        freqs = torch.outer(t, inv_freq)
        
        # LLaMA 风格: cat(cos, cos), cat(sin, sin) 不太一样
        # 标准 RoPE 是 interleaved [x1, x2, x3, x4] -> [-x2, x1, -x4, x3]
        # 但 LLaMA 是 sliced [x_half_1, x_half_2] -> [-x_half_2, x_half_1]
        # 我们这里实现 LLaMA 风格 (更适合 Triton 连续内存读取)
        
        emb = torch.cat((freqs, freqs), dim=-1)
        self.register_buffer("cos_cached", emb.cos().to(torch.float16))
        self.register_buffer("sin_cached", emb.sin().to(torch.float16))

    def forward(self, q, k):
        # q, k shape: [Batch, Seq, Num_Heads, Head_Dim]
        # 我们需要把它展平为 [Total_Heads, Head_Dim] 来并行处理
        # Total_Heads = Batch * Seq * Num_Heads
        
        batch, seq_len, n_heads, head_dim = q.shape
        assert head_dim == self.head_dim
        
        # 准备 Cos/Sin
        # 截取当前 seq_len 长度，并广播到 Batch 和 Heads
        # cos: [Seq, Dim] -> [Batch, Seq, Heads, Dim] -> Flatten
        # 为了 Triton 方便，我们在 Python 端做 expand (零拷贝)
        cos = self.cos_cached[:seq_len].unsqueeze(0).unsqueeze(2) # [1, Seq, 1, Dim]
        sin = self.sin_cached[:seq_len].unsqueeze(0).unsqueeze(2)
        
        cos = cos.expand(batch, seq_len, n_heads, head_dim).contiguous().view(-1, head_dim)
        sin = sin.expand(batch, seq_len, n_heads, head_dim).contiguous().view(-1, head_dim)
        
        # 准备输入输出
        q_flat = q.contiguous().view(-1, head_dim)
        k_flat = k.contiguous().view(-1, head_dim)
        
        q_out = torch.empty_like(q_flat)
        k_out = torch.empty_like(k_flat)
        
        # Grid
        n_rows = q_flat.shape[0]
        # Block Size 处理一半维度 (Head_Dim // 2)
        # 必须是 2 的幂
        BLOCK_SIZE = triton.next_power_of_2(head_dim // 2)
        
        # 启动 Kernel (Q)
        rope_kernel[(n_rows,)](
            q_flat, cos, sin, q_out,
            0, 0, head_dim, 1, # q strides (视为 1D array of rows)
            head_dim, 1,       # cos strides
            n_rows, head_dim,
            BLOCK_SIZE=BLOCK_SIZE
        )
        
        # 启动 Kernel (K)
        rope_kernel[(n_rows,)](
            k_flat, cos, sin, k_out,
            0, 0, head_dim, 1,
            head_dim, 1,
            n_rows, head_dim,
            BLOCK_SIZE=BLOCK_SIZE
        )
        
        return q_out.view(batch, seq_len, n_heads, head_dim), k_out.view(batch, seq_len, n_heads, head_dim)

# ==========================================
# 极限跑分
# ==========================================
if __name__ == "__main__":
    torch.manual_seed(0)
    
    # 模拟 Orion-0.1B 配置
    BATCH = 4
    SEQ = 2048
    HEADS = 16
    DIM = 64
    
    print(f"🚀 Benchmarking RoPE (Rotary Positional Embeddings)...")
    print(f"    Input: [{BATCH}, {SEQ}, {HEADS}, {DIM}]")
    
    if not torch.cuda.is_available(): exit(1)

    # 数据
    q = torch.randn(BATCH, SEQ, HEADS, DIM, device='cuda', dtype=torch.float16)
    k = torch.randn(BATCH, SEQ, HEADS, DIM, device='cuda', dtype=torch.float16)
    
    # 1. Ply RoPE
    ply_rope = PlyRoPE(DIM).cuda()
    
    # 2. PyTorch 原生实现 (LLaMA 风格)
    def apply_rotary_pos_emb(q, k, cos, sin):
        # cos, sin: [1, Seq, 1, Dim]
        q_embed = (q * cos) + (rotate_half(q) * sin)
        k_embed = (k * cos) + (rotate_half(k) * sin)
        return q_embed, k_embed

    def rotate_half(x):
        x1 = x[..., : x.shape[-1] // 2]
        x2 = x[..., x.shape[-1] // 2 :]
        return torch.cat((-x2, x1), dim=-1)

    # 预备 PyTorch 的 cos/sin
    cos_torch = ply_rope.cos_cached[:SEQ].unsqueeze(0).unsqueeze(2)
    sin_torch = ply_rope.sin_cached[:SEQ].unsqueeze(0).unsqueeze(2)
    
    # --- 验证 ---
    print("🔍 Validating...")
    pq, pk = ply_rope(q, k)
    tq, tk = apply_rotary_pos_emb(q, k, cos_torch, sin_torch)
    
    if torch.allclose(pq, tq, atol=1e-2, rtol=1e-2):
        print("✅ Correctness: PASSED")
    else:
        print("⚠️ Mismatch")
        print(f"   Max Diff: {(pq - tq).abs().max().item()}")

    # --- 性能 ---
    print("⏱️  Speed Test...")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    # PyTorch
    for _ in range(10): apply_rotary_pos_emb(q, k, cos_torch, sin_torch)
    start.record()
    for _ in range(100):
        apply_rotary_pos_emb(q, k, cos_torch, sin_torch)
    end.record()
    torch.cuda.synchronize()
    torch_ms = start.elapsed_time(end) / 100
    
    # Ply
    for _ in range(10): ply_rope(q, k)
    start.record()
    for _ in range(100):
        ply_rope(q, k)
    end.record()
    torch.cuda.synchronize()
    ply_ms = start.elapsed_time(end) / 100
    
    print("-" * 60)
    print(f"PyTorch RoPE: {torch_ms:.4f} ms")
    print(f"Ply RoPE:     {ply_ms:.4f} ms")
    print(f"⚡ Speedup: {torch_ms/ply_ms:.2f}x")
    print("-" * 60)

