"""Router implementations for Mixture of Experts."""

import torch
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod


class Router(nn.Module, ABC):
    """Base class for routers."""

    def __init__(self, input_dim: int, num_experts: int):
        super().__init__()
        self.input_dim = input_dim
        self.num_experts = num_experts

    @abstractmethod
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Compute routing weights.

        Args:
            x: Input tensor of shape (..., input_dim)

        Returns:
            Routing weights of shape (..., num_experts)
        """
        pass


class SoftMaxRouter(Router):
    """Softmax router that assigns a probability distribution over experts.

    Computes: softmax(x @ W)
    """

    def __init__(self, input_dim: int, num_experts: int):
        super().__init__(input_dim, num_experts)
        self.layer = nn.Linear(input_dim, num_experts)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.layer(x)
        return F.softmax(logits, dim=-1)
