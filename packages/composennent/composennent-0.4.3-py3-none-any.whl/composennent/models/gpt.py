"""GPT (Generative Pre-trained Transformer) implementation."""

import torch
import torch.nn as nn
from typing import Optional
from composennent.modules.decoders import Decoder
from composennent.modules.attention import causal_mask
from .nlp_base import BaseLanguageModel


class GPT(BaseLanguageModel):
    """GPT: Decoder-only Transformer for autoregressive language modeling.

    Implements a GPT-style architecture with stacked decoder layers,
    token embeddings, learned positional embeddings, and weight tying
    between the input embeddings and output projection.

    Args:
        vocab_size: Size of the vocabulary.
        latent_dim: Dimension of the model (embedding size).
        num_heads: Number of attention heads per layer.
        num_layers: Number of decoder layers.
        max_seq_len: Maximum sequence length. Defaults to 512.
        drop_out: Dropout probability. Defaults to 0.1.
        mlp_ratio: MLP expansion ratio for decoder layers. Defaults to 4.

    Example:
        >>> # Create new model
        >>> model = GPT(
        ...     vocab_size=50257,
        ...     latent_dim=768,
        ...     num_heads=12,
        ...     num_layers=12,
        ... )
        >>> logits = model(input_ids)  # (batch, seq_len, vocab_size)
        >>>
        >>> # Save model
        >>> model.save("gpt_model.pt")
        >>>
        >>> # Load pretrained model
        >>> loaded_model = GPT.load("gpt_model.pt")

    Note:
        Uses weight tying between token embeddings and language model head
        for improved parameter efficiency.
    """

    def __init__(
        self,
        vocab_size: int,
        latent_dim: int,
        num_heads: int,
        num_layers: int,
        max_seq_len: int = 512,
        drop_out: float = 0.1,
        mlp_ratio: int = 4,
        num_experts: int = 1,
        use_memory: bool = False,
        memory_size: int = 4096,
    ) -> None:
        super().__init__()


        self.vocab_size = vocab_size
        self.latent_dim = latent_dim
        self.num_heads = num_heads
        self.num_layers = num_layers
        self.max_seq_len = max_seq_len
        self.drop_out = drop_out
        self.mlp_ratio = mlp_ratio
        self.num_experts = num_experts
        
        # Initialize Memory if requested
        # We share one large memory store across all layers (or could be per layer, but shared is standard for RAG)
        self.use_memory = use_memory
        self.memory = None
        self.memory_head = None
        
        if use_memory:
            from composennent.modules.memory import KeyValueMemory, MemoryHead
            self.memory = KeyValueMemory(key_dim=latent_dim, value_dim=latent_dim, memory_size=memory_size)
            
            # The head that allows the model to write to its own memory
            self.memory_head = MemoryHead(hidden_dim=latent_dim, key_dim=latent_dim, value_dim=latent_dim)


        self.token_embedding = nn.Embedding(vocab_size, latent_dim)
        self.position_embedding = nn.Embedding(max_seq_len, latent_dim)
        self.dropout = nn.Dropout(drop_out)

        self.layers = nn.ModuleList([
            Decoder(
                latent_dim, 
                num_heads, 
                drop_out, 
                mlp_ratio, 
                num_experts=num_experts,
                # In standard RAG, we might only want memory in the upper layers, 
                # but here we'll keep it simple and pass it to all, or maybe just the last half?
                # Let's pass to all for consistent API, effectively making every layer able to "read".
                memory_component=self.memory
            )
            for _ in range(num_layers)
        ])

        self.ln_f = nn.LayerNorm(latent_dim)
        self.lm_head = nn.Linear(latent_dim, vocab_size, bias=False)

        self.lm_head.weight = self.token_embedding.weight

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        **kwargs,
    ) -> torch.Tensor:
        """Forward pass for language modeling.

        Args:
            input_ids: Token indices of shape (batch, seq_len).
            attention_mask: Attention mask (1=attend, 0=ignore).

        Returns:
            Logits over vocabulary of shape (batch, seq_len, vocab_size).
        """
        batch_size, seq_len = input_ids.shape
        positions = torch.arange(seq_len, device=input_ids.device).unsqueeze(0)

        x = self.token_embedding(input_ids) + self.position_embedding(positions)
        x = self.dropout(x)

        mask = causal_mask(seq_len, x.device)

        # Convert attention_mask (1=attend, 0=ignore) to key_padding_mask (True=ignore)
        key_padding_mask = None
        if attention_mask is not None:
            key_padding_mask = attention_mask == 0

        for layer in self.layers:
            x = layer(x, tgt_mask=mask, tgt_key_padding_mask=key_padding_mask)

        x = self.ln_f(x)
        logits = self.lm_head(x)
        
        # === SELF-MODIFYING MEMORY LOGIC ===
        # If enabled, check if the model wants to write to memory based on its FINAL thought (x)
        # We usually check only for the LAST token in the sequence during inference.
        if self.use_memory and self.memory_head is not None:
            # We look at the decision for the *last token*
            last_hidden_state = x[:, -1, :] # (batch, hidden_dim)
            
            gate, key, value = self.memory_head(last_hidden_state)
            
            # During inference, if gate is open, we write!
            if not self.training:
                # We can do this cleanly in a no_grad context context if we want, 
                # but memory.write already calls detach().
                
                # Check threshold (e.g., sigmoid > 0.5)
                # We iterate over batch to allow per-sample decision
                if (gate > 0.5).any():
                     # To keep batching simple in this demo, we write if ANY in batch trigger,
                     # or we filter. Memory.write expects full batch or we slice.
                     # Let's just always write but pass the 'gate' to memory?
                     # No, KeyValueMemory.write is hard-write.
                     # Let's filter indices where gate > 0.5
                     
                     mask = (gate > 0.5).squeeze(-1) # (batch,)
                     if mask.any():
                         self.memory.write(key[mask], value[mask])
        # ===================================

        return logits

    def save(self, path: str):
        """Save model weights and configuration."""
        super().save(path)

    @classmethod
    def load(cls, path: str, device: str = "cpu", **model_kwargs):
        """Load model from saved checkpoint."""
        return super().load(path, device=device, **model_kwargs)
