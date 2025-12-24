import torch
import torch.nn as nn
import ply # 复用我们已经打造的神兵利器

# ==========================================
# Ply 高性能 ViT Block
# ==========================================
# ViT 的核心结构与 LLM 惊人一致，我们可以直接复用算子
class PlyViTAttention(nn.Module):
    def __init__(self, dim, num_heads=8, qkv_bias=False, attn_drop=0., proj_drop=0.):
        super().__init__()
        self.num_heads = num_heads
        head_dim = dim // num_heads
        self.scale = head_dim ** -0.5

        # [Ply] 使用 v3.2 的 157 TFLOPS Linear
        self.qkv = ply.Linear(dim, dim * 3, bias=qkv_bias)
        self.attn_drop = nn.Dropout(attn_drop)
        
        # [Ply] 使用 v3.2 的 Linear
        self.proj = ply.Linear(dim, dim, bias=True) # ViT 通常 Output Proj 有 bias
        self.proj_drop = nn.Dropout(proj_drop)
        
        # [Ply] FlashAttention
        self.flash_attn = ply.FlashAttention()

    def forward(self, x):
        B, N, C = x.shape
        
        # [Ply] Fused QKV Projection
        qkv = self.qkv(x).reshape(B, N, 3, self.num_heads, C // self.num_heads).permute(2, 0, 3, 1, 4)
        q, k, v = qkv[0], qkv[1], qkv[2]

        # [Ply] FlashAttention expects [B, H, S, D]
        x = self.flash_attn(q, k, v)
        
        x = x.transpose(1, 2).reshape(B, N, C)
        x = self.proj(x)
        x = self.proj_drop(x)
        return x

class PlyMLP(nn.Module):
    def __init__(self, in_features, hidden_features=None, out_features=None, act_layer=nn.GELU, drop=0.):
        super().__init__()
        out_features = out_features or in_features
        hidden_features = hidden_features or in_features
        
        # [Ply] High-Performance Linear
        self.fc1 = ply.Linear(in_features, hidden_features, bias=True)
        self.act = act_layer()
        self.fc2 = ply.Linear(hidden_features, out_features, bias=True)
        self.drop = nn.Dropout(drop)

    def forward(self, x):
        x = self.fc1(x)
        x = self.act(x)
        x = self.drop(x)
        x = self.fc2(x)
        x = self.drop(x)
        return x

class PlyViTBlock(nn.Module):
    def __init__(self, dim, num_heads, mlp_ratio=4., qkv_bias=False, drop=0., attn_drop=0., act_layer=nn.GELU, norm_layer=nn.LayerNorm):
        super().__init__()
        # [Ply] 如果追求极致带宽，这里可以换成 ply.RMSNorm
        # 但标准 ViT 用 LayerNorm，为了兼容性暂且保留，可随时替换
        self.norm1 = norm_layer(dim)
        self.attn = PlyViTAttention(dim, num_heads=num_heads, qkv_bias=qkv_bias, attn_drop=attn_drop, proj_drop=drop)
        self.drop_path = nn.Identity() # 简化演示
        
        self.norm2 = norm_layer(dim)
        mlp_hidden_dim = int(dim * mlp_ratio)
        self.mlp = PlyMLP(in_features=dim, hidden_features=mlp_hidden_dim, act_layer=act_layer, drop=drop)

    def forward(self, x):
        x = x + self.drop_path(self.attn(self.norm1(x)))
        x = x + self.drop_path(self.mlp(self.norm2(x)))
        return x

# ==========================================
# 简单的 ViT 模型入口
# ==========================================
class PlyVisionTransformer(nn.Module):
    def __init__(self, img_size=224, patch_size=16, in_chans=3, num_classes=1000, embed_dim=768, depth=12, num_heads=12):
        super().__init__()
        # 简单的 Patch Embedding (可以用 Conv2d 实现)
        self.patch_embed = nn.Conv2d(in_chans, embed_dim, kernel_size=patch_size, stride=patch_size)
        num_patches = (img_size // patch_size) ** 2
        
        self.cls_token = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed = nn.Parameter(torch.zeros(1, num_patches + 1, embed_dim))
        self.pos_drop = nn.Dropout(p=0.0)

        # [Ply] 核心 Block 堆叠
        self.blocks = nn.ModuleList([
            PlyViTBlock(dim=embed_dim, num_heads=num_heads)
            for _ in range(depth)])
            
        self.norm = nn.LayerNorm(embed_dim)
        # [Ply] Head Linear
        self.head = ply.Linear(embed_dim, num_classes, bias=True)

    def forward(self, x):
        B = x.shape[0]
        x = self.patch_embed(x).flatten(2).transpose(1, 2) # [B, C, H, W] -> [B, N, C]
        
        cls_tokens = self.cls_token.expand(B, -1, -1)
        x = torch.cat((cls_tokens, x), dim=1)
        x = x + self.pos_embed
        x = self.pos_drop(x)

        for blk in self.blocks:
            x = blk(x)

        x = self.norm(x)
        x = x[:, 0] # CLS token
        x = self.head(x)
        return x
