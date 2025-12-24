"""Models module with shared capabilities and architecture definitions.

Usage:
    from composennent.models import GPT, BERT, BaseModel
    
    model = GPT(vocab_size=1000, latent_dim=512)
"""

from .base import BaseModel
from .nlp_base import BaseLanguageModel
from .gpt import GPT
from .bert import BERT
from .transformer import Transformer

__all__ = [
    "BaseModel", 
    "BaseLanguageModel",
    "GPT", 
    "BERT", 
    "Transformer"
]
