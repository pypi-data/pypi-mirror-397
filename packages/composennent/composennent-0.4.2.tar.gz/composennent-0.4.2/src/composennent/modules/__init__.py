"""Modules: The building blocks of Composennent.

This module consolidates all layers, embeddings, blocks, and mechanism implementations.
"""

# Core blocks
from .block import Block
from .sequential import SequentialBlock

# Layer Types
from .encoders import (
    encoder,
    BidirectionalEncoder,
    Encoder,
    ENCODERS
)
from .decoders import (
    decoder,
    CausalDecoder,
    CrossAttentionDecoder,
    Decoder,
    DECODERS
)
from .embeddings import (
    embedding,
    TokenEmbedding,
    PatchEmbedding,
    FeatureEmbedding,
    EMBEDDINGS
)
from .positional import (
    positional_encoding,
    AbsolutePositionalEncoding,
    RelativePositionalEncoding,
    RotaryPositionalEncoding,
    PositionalEncoding,
    POSITIONAL_ENCODINGS
)

# Note: Residuals are usually handled inside blocks or via simple add.

# Mechanisms
from .attention import (
    MultiHeadAttention,
    # causal_mask, padding_mask are useful utilities
    causal_mask,
    padding_mask
)
from .feedforward import (
    MLP,
    GLU,
    GEGLU,
    SwiGLU,
    ReGLU
)
from .experts import (
    ContextDependentSoftExpertLayer,
    # Router if exposed
)
