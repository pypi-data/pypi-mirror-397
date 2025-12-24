import torch
import triton
import triton.language as tl

# ==========================================
# 核心引擎: Paged Attention Kernel (Decoding Phase)
# ==========================================
@triton.jit
def paged_attention_kernel(
    Q_ptr,              
    K_Cache_ptr,        
    V_Cache_ptr,        
    Block_Tables_ptr,   
    Context_Lens_ptr,   
    Out_ptr,            
    stride_q_b, stride_q_h, stride_q_d,
    stride_kb_n, stride_kb_s, stride_kb_h, stride_kb_d, 
    stride_vb_n, stride_vb_s, stride_vb_h, stride_vb_d,
    stride_bt_b, stride_bt_s, 
    stride_o_b, stride_o_h, stride_o_d,
    sm_scale,
    Block_Size: tl.constexpr,
    Head_Dim: tl.constexpr,
    BLOCK_DMODEL: tl.constexpr, 
    BLOCK_N: tl.constexpr,      
):
    pid_h = tl.program_id(0)
    pid_b = tl.program_id(1)
    
    # 1. Load Query
    q_offset = pid_b * stride_q_b + pid_h * stride_q_h
    offs_d = tl.arange(0, BLOCK_DMODEL)
    q_ptrs = Q_ptr + q_offset + offs_d * stride_q_d
    q = tl.load(q_ptrs, mask=offs_d < Head_Dim, other=0.0)
    
    # 2. Accumulator
    m_i = -float("inf")
    l_i = 0.0
    acc = tl.zeros([BLOCK_DMODEL], dtype=tl.float32)
    
    # 3. Context Info
    context_len = tl.load(Context_Lens_ptr + pid_b)
    num_logical_blocks = (context_len + Block_Size - 1) // Block_Size
    
    # 4. Loop Blocks
    bt_ptr_base = Block_Tables_ptr + pid_b * stride_bt_b
    
    for block_idx in range(0, num_logical_blocks):
        physical_block_id = tl.load(bt_ptr_base + block_idx * stride_bt_s)
        
        block_offset_k = physical_block_id * stride_kb_n
        block_offset_v = physical_block_id * stride_vb_n
        
        offs_s = tl.arange(0, Block_Size)
        current_logical_start = block_idx * Block_Size
        token_mask = (current_logical_start + offs_s) < context_len
        
        k_ptrs = K_Cache_ptr + block_offset_k + \
                 offs_s[:, None] * stride_kb_s + \
                 pid_h * stride_kb_h + \
                 offs_d[None, :] * stride_kb_d
                 
        k = tl.load(k_ptrs, mask=token_mask[:, None] & (offs_d[None, :] < Head_Dim), other=0.0)
        
        qk = tl.sum(q[None, :] * k, axis=1)
        qk *= sm_scale
        
        qk = tl.where(token_mask, qk, float("-inf"))
        m_i_new = tl.max(qk, 0)
        m_i_new = tl.maximum(m_i, m_i_new)
        p = tl.exp(qk - m_i_new)
        alpha = tl.exp(m_i - m_i_new)
        acc *= alpha
        l_i *= alpha
        
        v_ptrs = V_Cache_ptr + block_offset_v + \
                 offs_s[:, None] * stride_vb_s + \
                 pid_h * stride_vb_h + \
                 offs_d[None, :] * stride_vb_d
        v = tl.load(v_ptrs, mask=token_mask[:, None] & (offs_d[None, :] < Head_Dim), other=0.0)
        
        acc += tl.sum(p[:, None] * v, axis=0)
        l_i += tl.sum(p, 0)
        m_i = m_i_new

    acc = acc / l_i
    out_ptrs = Out_ptr + pid_b * stride_o_b + pid_h * stride_o_h + offs_d * stride_o_d
    tl.store(out_ptrs, acc.to(tl.float16), mask=offs_d < Head_Dim)

# ==========================================
# 2. PlyPagedAttention Manager
# ==========================================
class PlyPagedAttentionManager(torch.nn.Module):
    def __init__(self, num_blocks, block_size, num_heads, head_dim):
        super().__init__()
        self.block_size = block_size
        self.num_heads = num_heads
        self.head_dim = head_dim
        
        self.k_cache = torch.zeros(num_blocks, block_size, num_heads, head_dim, 
                                   device='cuda', dtype=torch.float16)
        self.v_cache = torch.zeros(num_blocks, block_size, num_heads, head_dim, 
                                   device='cuda', dtype=torch.float16)
        
    def forward(self, q, block_tables, context_lens):
        batch_size = q.shape[0]
        out = torch.empty_like(q)
        sm_scale = 1.0 / (self.head_dim ** 0.5)
        
        grid = (self.num_heads, batch_size)
        
        paged_attention_kernel[grid](
            q, self.k_cache, self.v_cache,
            block_tables, context_lens,
            out,
            q.stride(0), q.stride(1), q.stride(2),
            self.k_cache.stride(0), self.k_cache.stride(1), self.k_cache.stride(2), self.k_cache.stride(3),
            self.v_cache.stride(0), self.v_cache.stride(1), self.v_cache.stride(2), self.v_cache.stride(3),
            block_tables.stride(0), block_tables.stride(1),
            out.stride(0), out.stride(1), out.stride(2),
            sm_scale,
            Block_Size=self.block_size,
            Head_Dim=self.head_dim,
            BLOCK_DMODEL=triton.next_power_of_2(self.head_dim),
            BLOCK_N=self.block_size
        )
        return out

# ==========================================
# 3. 验证与跑分
# ==========================================
if __name__ == "__main__":
    torch.manual_seed(0)
    
    BATCH = 4
    HEADS = 32
    DIM = 128
    BLOCK_SIZE = 16
    MAX_CONTEXT = 4096 
    NUM_PHYSICAL_BLOCKS = 1024 
    
    print(f"🚀 Benchmarking Ply PagedAttention (Decoding Phase)...")
    print(f"    Hardware: RTX 5090")
    
    if not torch.cuda.is_available(): exit(1)
    
    manager = PlyPagedAttentionManager(NUM_PHYSICAL_BLOCKS, BLOCK_SIZE, HEADS, DIM).cuda()
    
    q = torch.randn(BATCH, HEADS, DIM, device='cuda', dtype=torch.float16)
    
    block_tables = torch.zeros(BATCH, MAX_CONTEXT // BLOCK_SIZE, dtype=torch.int32, device='cuda')
    context_lens = torch.full((BATCH,), MAX_CONTEXT, dtype=torch.int32, device='cuda')
    
    for b in range(BATCH):
        start_block = b * (MAX_CONTEXT // BLOCK_SIZE)
        for i in range(MAX_CONTEXT // BLOCK_SIZE):
            phys_id = start_block + i
            block_tables[b, i] = phys_id
            manager.k_cache[phys_id].uniform_(-1, 1)
            manager.v_cache[phys_id].uniform_(-1, 1)
            
    # --- 验证 ---
    print("🔍 Validating...")
    k_cont = torch.empty(BATCH, MAX_CONTEXT, HEADS, DIM, device='cuda', dtype=torch.float16)
    v_cont = torch.empty(BATCH, MAX_CONTEXT, HEADS, DIM, device='cuda', dtype=torch.float16)
    
    for b in range(BATCH):
        for i in range(MAX_CONTEXT // BLOCK_SIZE):
            phys_id = block_tables[b, i]
            k_cont[b, i*BLOCK_SIZE : (i+1)*BLOCK_SIZE] = manager.k_cache[phys_id]
            v_cont[b, i*BLOCK_SIZE : (i+1)*BLOCK_SIZE] = manager.v_cache[phys_id]
            
    # [FIXED] 正确的维度变换，避免广播
    # Q: [B, H, D] -> [B, H, 1, D] (Head 维度对齐，Seq 维度为 1)
    q_in = q.unsqueeze(2) 
    
    # K/V: [B, S, H, D] -> [B, H, S, D]
    k_in = k_cont.transpose(1, 2)
    v_in = v_cont.transpose(1, 2)
    
    ref_out = torch.nn.functional.scaled_dot_product_attention(q_in, k_in, v_in)
    
    # ref_out: [B, H, 1, D] -> [B, H, D]
    ref_out = ref_out.reshape(BATCH, HEADS, DIM)
    
    ply_out = manager(q, block_tables, context_lens)
    
    if torch.allclose(ply_out, ref_out, atol=1e-1, rtol=1e-1):
        print("✅ Correctness: PASSED")
    else:
        print("⚠️ Mismatch")
        print(f"   Max Diff: {(ply_out - ref_out).abs().max().item()}")
        
    # --- 测速 ---
    print("⏱️  Speed Test (Decoding 1 token over 4k context)...")
    start = torch.cuda.Event(enable_timing=True)
    end = torch.cuda.Event(enable_timing=True)
    
    # PyTorch SDPA (Ideal)
    for _ in range(10): torch.nn.functional.scaled_dot_product_attention(q_in, k_in, v_in)
    start.record()
    for _ in range(100):
        torch.nn.functional.scaled_dot_product_attention(q_in, k_in, v_in)
    end.record()
    torch.cuda.synchronize()
    torch_ms = start.elapsed_time(end) / 100
    
    # Ply PagedAttention
    for _ in range(10): manager(q, block_tables, context_lens)
    start.record()
    for _ in range(100):
        manager(q, block_tables, context_lens)
    end.record()
    torch.cuda.synchronize()
    ply_ms = start.elapsed_time(end) / 100
    
    print("-" * 60)
    print(f"Standard Attention (Ideal Contiguous): {torch_ms:.4f} ms")
    print(f"Ply PagedAttention (Non-Contiguous):   {ply_ms:.4f} ms")
    print(f"⚡ Relative Speed: {100 * torch_ms / ply_ms:.1f}%")
    print("-" * 60)

