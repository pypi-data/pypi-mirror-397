"""Expert layers for Context-Dependent Mixture of Experts."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, List

from composennent.modules.block import Block
from composennent.modules.experts.router import SoftMaxRouter


class ContextDependentSoftExpertLayer(Block):
    """Context-Dependent Expert Layer with Soft Masking.

    This layer implements "Method 1: Soft parameter masking" where:
    1. A shared backbone (SwiGLU) holds the parameters.
    2. Multiple "mask generators" create dynamic masks for the shared weights.
    3. A router determines how much each "virtual expert" contributes.

    Args:
        latent_dim: Input/Output dimension of the model.
        num_experts: Number of virtual experts.
        mlp_ratio: Expansion ratio for the internal FFN. Defaults to 4.
        dropout: Dropout probability. Defaults to 0.1.
    """

    def __init__(
        self,
        latent_dim: int,
        num_experts: int,
        mlp_ratio: int = 4,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.latent_dim = latent_dim
        self.num_experts = num_experts
        self.mlp_ratio = mlp_ratio

        hidden_dim = latent_dim * mlp_ratio

        # Router to mix virtual experts
        self.router = SoftMaxRouter(latent_dim, num_experts)

        # Shared parameters (SwiGLU style w1, w2, w3)
        # Note: We keep them as Linear but we will apply masks to their weights manually if needed,
        # or more efficiently, we apply masks to the INTERMEDIATE activations or weights.
        
        # User request: "Masks = [torch.sigmoid(gen(x)) for gen in mask_generators]"
        # "masked_weight = self.shared_params.weight * mask"
        
        # To make this efficient and mathematically consistent with the user's idea:
        # We will have ONE shared set of W1, W2, W3 weights.
        # But for each expert, we generate a mask that modulates these weights.
        # Doing weight masking at runtime is expensive (num_experts * huge_matrix).
        # Let's interpret the user's "mask" as potentially an activation mask or rank-1 weight mask.
        
        # Implementation of "Method 1" exactly as described by user:
        # masks = sigmoid(gen(x)) -> shape (B, D) or (B, H)
        # masked_weight = shared.weight * mask -> efficient only if mask is vector (broadcast)
        # Here we assume mask acts on the Hidden Dimension of the FFN.
        
        self.w1 = nn.Linear(latent_dim, hidden_dim, bias=False)
        self.w2 = nn.Linear(latent_dim, hidden_dim, bias=False)
        self.w3 = nn.Linear(hidden_dim, latent_dim, bias=False)
        
        # Mask generators: One per expert. They generate masks for the HIDDEN dim.
        # This allows specialization of which neurons fire in the FFN.
        self.mask_generators = nn.ModuleList([
            nn.Linear(latent_dim, hidden_dim) 
            for _ in range(num_experts)
        ])
        
        self.dropout = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.
        
        Args:
            x: Input tensor (batch, seq, latent_dim)
        """
        # 1. Routing weights: (batch, seq, num_experts)
        routing_weights = self.router(x)
        
        # 2. Compute raw shared SwiGLU activations
        # SwiGLU(x) = (xW1) * SiLU(xW2)
        # We compute these ONCE for the shared params.
        gate = self.w1(x)       # (batch, seq, hidden)
        val = self.w2(x)        # (batch, seq, hidden)
        
        # 3. For each expert, apply a mask to the HIDDEN activations
        # This acts effectively like masking the weights w1/w2 projecting TO hidden.
        # mask_i = sigmoid(gen_i(x))
        
        expert_outputs = []
        
        for i in range(self.num_experts):
            # Generate mask for this expert: (batch, seq, hidden)
            # We use sigmoid to make it a soft gate (0 to 1)
            mask = torch.sigmoid(self.mask_generators[i](x))
            
            # Apply mask to the shared activations ("Expert i's view of the features")
            # expert_gate = gate * mask
            # expert_val = val * mask
            # In SwiGLU, often we mask the result of the element-wise prod or the inputs.
            # Let's mask the 'gate' and 'val' independently or the combined activation?
            # User sample: "masked_weight = shared.weight * mask"
            # Equivalent to: activations * mask
            
            # Let's apply mask to the silicon-gated activation specifically
            # act = (gate * mask) * SiLU(val * mask) ? 
            # Or simplified: act = (gate * silu(val)) * mask
            # The second one means the expert just selects subsets of the global activation.
            # Scaling it by the mask allows "turning off" neurons for this expert.
            
            pre_activation = F.silu(gate) * val
            masked_activation = pre_activation * mask
            
            # Apply W3 (Project back to latent)
            # This is "Expert i's output"
            out = self.w3(masked_activation)
            expert_outputs.append(out)
            
        # 4. Weighted combination
        # sum(routing_prob_i * expert_out_i)
        
        # Stack experts: (batch, seq, num_experts, latent)
        expert_outputs = torch.stack(expert_outputs, dim=-2)
        
        # Expand routing weights for broadcast: (batch, seq, num_experts, 1)
        routing_weights = routing_weights.unsqueeze(-1)
        
        # Weighted sum
        output = torch.sum(expert_outputs * routing_weights, dim=-2)
        
        return self.dropout(output)
