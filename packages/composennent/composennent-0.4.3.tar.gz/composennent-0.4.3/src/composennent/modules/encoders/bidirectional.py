"""Transformer Encoder block implementation."""

import torch
import torch.nn as nn
from typing import Optional

from composennent.modules.block import Block
from composennent.modules.sequential import SequentialBlock
from composennent.modules.attention import MultiHeadAttention


from composennent.modules.experts.expert_layer import ContextDependentSoftExpertLayer


class BidirectionalEncoder(Block):
    """Bidirectional Encoder block (Transformer-style).
    
    Implements a standard bidirectional Transformer encoder layer with:
    - Multi-head self-attention
    - Feed-forward network (MLP)

    Uses pre-LayerNorm architecture for improved training stability.

    Args:
        latent_dim: Dimension of the model (embedding size).
        num_heads: Number of attention heads.
        dropout: Dropout probability. Defaults to 0.1.
        mlp_ratio: Expansion ratio for MLP hidden dimension. Defaults to 4.
        return_attention: Whether to return attention weights. Defaults to False.
        num_experts: Number of context-dependent experts. Defaults to 1 (standard MLP).

    Example:
        >>> enc = BidirectionalEncoder(latent_dim=512, num_heads=8)
        >>> output = enc(x)
    """

    def __init__(
        self,
        latent_dim: int,
        num_heads: int,
        dropout: float = 0.1,
        mlp_ratio: int = 4,
        return_attention: bool = False,
        num_experts: int = 1,
    ) -> None:
        super().__init__()
        self.latent_dim = latent_dim
        self.return_attention = return_attention

        self.self_attn = MultiHeadAttention(
            embed_dim=latent_dim,
            num_heads=num_heads,
            dropout=dropout,
        )
        self.norm1 = nn.LayerNorm(latent_dim)
        
        if num_experts > 1:
            self.mlp = ContextDependentSoftExpertLayer(
                latent_dim=latent_dim,
                num_experts=num_experts,
                mlp_ratio=mlp_ratio,
                dropout=dropout,
            )
        else:
            mlp_hidden_dim = latent_dim * mlp_ratio
            self.mlp = SequentialBlock(
                nn.Linear(latent_dim, mlp_hidden_dim),
                nn.GELU(),
                nn.Dropout(dropout),
                nn.Linear(mlp_hidden_dim, latent_dim),
            )
        self.norm2 = nn.LayerNorm(latent_dim)
        self.dropout_layer = nn.Dropout(dropout)

    def forward(
        self,
        x: torch.Tensor,
        key_padding_mask: Optional[torch.Tensor] = None,
        attn_mask: Optional[torch.Tensor] = None,
        return_attention: Optional[bool] = None,
    ):
        return_attn = return_attention if return_attention is not None else self.return_attention

        normed = self.norm1(x)
        attn_out, attn_weights = self.self_attn(
            normed,
            attn_mask=attn_mask,
            key_padding_mask=key_padding_mask,
            need_weights=return_attn,
        )
        x = x + self.dropout_layer(attn_out)

        normed = self.norm2(x)
        mlp_out = self.mlp(normed)
        x = x + self.dropout_layer(mlp_out)

        return (x, attn_weights) if return_attn else x
