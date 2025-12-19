import torch
import pytest
from composennent.modules.memory import KeyValueMemory, RetrievalBlock

def test_key_value_memory_write_read():
    # Setup
    mem = KeyValueMemory(key_dim=16, value_dim=32, memory_size=10)
    
    # Create fake data
    keys = torch.randn(2, 16) # Batch of 2
    values = torch.randn(2, 32)
    
    # Write to memory
    mem.write(keys, values)
    
    # Check if written (simple check: pointers updated? values exist?)
    assert mem.write_pointer == 2
    assert not torch.all(mem.keys == 0)
    
    # Read back using similar keys
    # If we query with the EXACT same keys, we should get high weight on those slots
    retrieved, weights = mem.read(keys)
    
    assert retrieved.shape == (2, 32)
    
    # The weight on the correct index (0 and 1) should be high
    # Since we initialized with zeros, only indices 0 and 1 have non-zero keys/values.
    # Dot product with zeros is 0. Dot product with matching vector is high.
    # So softmax should peak at 0 for item 0, and 1 for item 1.
    assert torch.argmax(weights[0]) == 0
    assert torch.argmax(weights[1]) == 1

def test_retrieval_block_forward():
    # Setup
    mem = KeyValueMemory(key_dim=16, value_dim=32, memory_size=10)
    block = RetrievalBlock(hidden_dim=16, memory_component=mem)
    
    # Create fake inputs
    hidden_states = torch.randn(2, 5, 16) # (Batch, Seq, Hidden)
    
    # Add some memory content first so retrieval isn't just noise
    mem.write(torch.randn(2, 16), torch.randn(2, 32))
    
    # Forward pass
    output = block(hidden_states)
    
    # Check shape maintenance
    assert output.shape == (2, 5, 16)

if __name__ == "__main__":
    test_key_value_memory_write_read()
    test_retrieval_block_forward()
