import torch
from composennent.models.gpt import GPT

def test_gpt_autonomous_write():
    # Setup model with memory
    model = GPT(
        vocab_size=100,
        latent_dim=32,
        num_heads=4,
        num_layers=2,
        use_memory=True,
        memory_size=10
    )
    model.eval() # Must be in eval mode for autonomous writing to trigger by default
    
    # 1. Force the memory head to output "WRITE!" (Gate > 0.5)
    # Since weights are random, we manually bias the bias.
    with torch.no_grad():
        model.memory_head.write_gate.bias.fill_(10.0) # Sigmoid(10) ~= 0.999
    
    # Check memory is empty (all zeros initially)
    # The usage counter isn't strictly implemented with a counter that resets, 
    # but the content is zero.
    assert torch.all(model.memory.keys == 0)
    
    # 2. Run Forward Pass
    input_ids = torch.randint(0, 100, (1, 5)) # Single batch
    model(input_ids)
    
    # 3. Check if memory was written to
    # Since we forced the gate to be high, it should have written the key/value projected
    # from the last token's hidden state.
    # We can just check if keys are non-zero now.
    assert not torch.all(model.memory.keys == 0)
    
    print("Autonomous write test passed: Model wrote to memory!")

if __name__ == "__main__":
    test_gpt_autonomous_write()
