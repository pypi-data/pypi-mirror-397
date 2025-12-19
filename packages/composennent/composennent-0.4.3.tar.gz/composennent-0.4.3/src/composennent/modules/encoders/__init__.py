"""Encoder blocks for transformer models.

Usage:
    # Via factory function
    enc = encoder("transformer", latent_dim=512, num_heads=8)
    
    # Direct import
    from composennent.modules.encoders import TransformerEncoder
"""

from typing import Dict, Any, Type
from .bidirectional import BidirectionalEncoder

# Registry of encoder types
ENCODERS: Dict[str, Type] = {
    "bidirectional": BidirectionalEncoder,
    "transformer": BidirectionalEncoder,  # alias
    "bert": BidirectionalEncoder,  # alias
}


def encoder(encoder_type: str, **kwargs) -> Any:
    """Create an encoder by type name.
    
    Args:
        encoder_type: One of "bidirectional", "transformer"
        **kwargs: Arguments passed to the encoder class
        
    Returns:
        Encoder instance
        
    Example:
        >>> enc = encoder("bidirectional", latent_dim=512, num_heads=8)
    """
    if encoder_type not in ENCODERS:
        available = ", ".join(f'"{k}"' for k in ENCODERS.keys())
        raise ValueError(f"Unknown encoder type: '{encoder_type}'. Choose from: {available}")
    return ENCODERS[encoder_type](**kwargs)


# Aliases for backward compatibility
TransformerEncoder = BidirectionalEncoder
Encoder = BidirectionalEncoder

__all__ = ["encoder", "BidirectionalEncoder", "TransformerEncoder", "Encoder", "ENCODERS"]
