import torch
import pytest
from composennent.models.gpt import GPT

def test_gpt_with_memory_initialization():
    # Test that we can initialize GPT with memory
    model = GPT(
        vocab_size=100,
        latent_dim=32,
        num_heads=4,
        num_layers=2,
        use_memory=True,
        memory_size=50
    )
    
    # Check if memory exists
    assert model.memory is not None
    assert model.memory.keys.shape == (50, 32)
    
    # Check if memory is propagated to layers
    # We passed it to all layers in our implementation
    assert hasattr(model.layers[0], 'retrieval_block')
    assert model.layers[0].retrieval_block.memory is model.memory

def test_gpt_with_memory_forward():
    # Test forward pass
    model = GPT(
        vocab_size=100,
        latent_dim=32,
        num_heads=4,
        num_layers=2,
        use_memory=True,
        memory_size=50
    )
    
    input_ids = torch.randint(0, 100, (2, 10)) # (Batch, Seq)
    
    # Add a fact to memory just to be sure
    key = torch.randn(1, 32)
    val = torch.randn(1, 32)
    model.memory.write(key, val)
    
    # Run forward
    logits = model(input_ids)
    
    assert logits.shape == (2, 10, 100)

if __name__ == "__main__":
    test_gpt_with_memory_initialization()
    test_gpt_with_memory_forward()
