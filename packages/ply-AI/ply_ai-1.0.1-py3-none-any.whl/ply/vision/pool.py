import torch
import torch.nn as nn
import triton
import triton.language as tl
import ply

@triton.jit
def max_pool2d_nhwc_kernel(
    x_ptr, y_ptr,
    N, H, W, C,
    H_out, W_out,
    stride_h, stride_w,
    kernel_h, kernel_w,
    BLOCK_N: tl.constexpr, BLOCK_C: tl.constexpr,
):
    pid_n = tl.program_id(0)
    pid_hw = tl.program_id(1)
    pid_c = tl.program_id(2)
    
    offs_n = pid_n * BLOCK_N + tl.arange(0, BLOCK_N)
    offs_c = pid_c * BLOCK_C + tl.arange(0, BLOCK_C)
    mask_n = offs_n < N
    mask_c = offs_c < C
    
    h_out = pid_hw // W_out
    w_out = pid_hw % W_out
    
    h_in_start = h_out * stride_h
    w_in_start = w_out * stride_w
    
    max_val = tl.full((BLOCK_N, BLOCK_C), value=float('-inf'), dtype=tl.float32)
    
    # 指针计算优化: 提取不变部分
    # x_ptr offset = (n * H*W + h * W + w) * C + c
    # stride_n_in = H * W * C
    
    for kh in range(kernel_h):
        for kw in range(kernel_w):
            h_in = h_in_start + kh
            w_in = w_in_start + kw
            
            mask_in_bounds = (h_in >= 0) & (h_in < H) & (w_in >= 0) & (w_in < W)
            
            # 计算 offset
            # block_offset_n = offs_n * (H * W * C)
            # block_offset_c = offs_c
            # pixel_offset = (h_in * W + w_in) * C
            
            offs_x = (
                offs_n[:, None] * (H * W * C) +
                (h_in * W + w_in) * C + 
                offs_c[None, :]
            )
            
            val = tl.load(x_ptr + offs_x, mask=mask_n[:, None] & mask_c[None, :] & mask_in_bounds, other=float('-inf'))
            max_val = tl.maximum(max_val, val)
            
    # Store
    offs_y = (
        offs_n[:, None] * (H_out * W_out * C) +
        (h_out * W_out + w_out) * C +
        offs_c[None, :]
    )
    tl.store(y_ptr + offs_y, max_val, mask=mask_n[:, None] & mask_c[None, :])

class PlyMaxPool2d(nn.Module):
    def __init__(self, kernel_size, stride=None, padding=0):
        super().__init__()
        self.kernel_size = kernel_size if isinstance(kernel_size, tuple) else (kernel_size, kernel_size)
        self.stride = stride if stride is not None else self.kernel_size
        self.stride = self.stride if isinstance(self.stride, tuple) else (self.stride, self.stride)
        assert padding == 0, "PlyMaxPool2d currently only supports padding=0"

    def forward(self, x):
        # 强制转换为 Channels Last (NHWC) 内存格式，这是 Tensor Core 友好的格式
        if not x.is_contiguous(memory_format=torch.channels_last):
            x = x.contiguous(memory_format=torch.channels_last)
            
        N, C, H, W = x.shape
        KH, KW = self.kernel_size
        SH, SW = self.stride
        
        H_out = (H - KH) // SH + 1
        W_out = (W - KW) // SW + 1
        
        y = torch.empty((N, C, H_out, W_out), device=x.device, dtype=x.dtype, memory_format=torch.channels_last)
        
        # Grid: [N_blocks, H_out*W_out, C_blocks]
        BLOCK_N = 16
        BLOCK_C = 64
        grid = (triton.cdiv(N, BLOCK_N), H_out * W_out, triton.cdiv(C, BLOCK_C))
        
        max_pool2d_nhwc_kernel[grid](
            x, y,
            N, H, W, C,
            H_out, W_out,
            SH, SW,
            KH, KW,
            BLOCK_N=BLOCK_N, BLOCK_C=BLOCK_C
        )
        return y
