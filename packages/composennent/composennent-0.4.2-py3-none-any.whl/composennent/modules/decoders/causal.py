"""Causal Decoder block (GPT-style, self-attention only)."""

import torch
import torch.nn as nn
from typing import Optional

from composennent.modules.block import Block
from composennent.modules.sequential import SequentialBlock
from composennent.modules.attention import MultiHeadAttention


from composennent.modules.experts.expert_layer import ContextDependentSoftExpertLayer
from composennent.modules.memory import KeyValueMemory, RetrievalBlock


class CausalDecoder(Block):
    """Causal Decoder block for autoregressive generation (GPT-style).

    Uses only self-attention (no self-attention). Suitable for:
    - GPT-style language models
    - Decoder-only architectures (LLaMA, Mistral)

    Args:
        latent_dim: Dimension of the model.
        num_heads: Number of attention heads.
        dropout: Dropout probability. Defaults to 0.1.
        mlp_ratio: MLP expansion ratio. Defaults to 4.
        return_attention: Whether to return attention weights.
        num_experts: Number of context-dependent experts. Defaults to 1 (standard MLP).
        memory_component: Optional KeyValueMemory instance. 
                          If provided, a RetrievalBlock is added.

    Example:
        >>> dec = CausalDecoder(latent_dim=512, num_heads=8)
        >>> output = dec(x, tgt_mask=causal_mask)
    """

    def __init__(
        self,
        latent_dim: int,
        num_heads: int,
        dropout: float = 0.1,
        mlp_ratio: int = 4,
        return_attention: bool = False,
        num_experts: int = 1,
        memory_component: Optional[KeyValueMemory] = None,
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

        # Memory Integration
        if memory_component is not None:
             self.retrieval_block = RetrievalBlock(
                 hidden_dim=latent_dim,
                 memory_component=memory_component
             )

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
        tgt_mask: Optional[torch.Tensor] = None,
        tgt_key_padding_mask: Optional[torch.Tensor] = None,
        return_attention: Optional[bool] = None,
    ):
        return_attn = return_attention if return_attention is not None else self.return_attention

        normed = self.norm1(x)
        attn_out, attn_weights = self.self_attn(
            normed,
            attn_mask=tgt_mask,
            key_padding_mask=tgt_key_padding_mask,
            need_weights=return_attn,
        )
        x = x + self.dropout_layer(attn_out)

        # === MEMORY LAYER ===
        # If this decoder block has memory attached, use it here.
        if hasattr(self, 'retrieval_block'):
            # The retrieval block has its own residual connection inside usually,
            # but let's check implementation. Our RetrievalBlock DOES have residual.
            # So we just pass x through it.
            x = self.retrieval_block(x)
        # ====================

        normed = self.norm2(x)
        mlp_out = self.mlp(normed)
        x = x + self.dropout_layer(mlp_out)

        return (x, attn_weights) if return_attn else x
