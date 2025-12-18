
import pytest
import torch
import torch.nn as nn
from unittest.mock import MagicMock
from composennent.nlp.transformers.base import BaseLanguageModel

class MockModel(BaseLanguageModel):
    def __init__(self, vocab_size=10):
        super().__init__()
        self.vocab_size = vocab_size
        self.max_seq_len = 20
        # Mock parameters to allow device inference
        self.dummy_param = nn.Parameter(torch.empty(0))

    def forward(self, input_ids, **kwargs):
        # Always return logits where token 1 is highest, then 2, etc.
        batch_size, seq_len = input_ids.shape
        logits = torch.zeros(batch_size, seq_len, self.vocab_size)
        
        # Make token 1 the most likely by default
        logits[:, :, 1] = 10.0
        logits[:, :, 2] = 5.0
        logits[:, :, 0] = 0.0
        
        return logits

def test_generate_accepts_repetition_penalty():
    """Test that generate accepts repetition_penalty argument."""
    model = MockModel()
    tokenizer = MagicMock()
    tokenizer.encode.return_value = [0]
    tokenizer.decode.return_value = "text"
    
    # Should not raise error
    model.generate(
        "input", 
        tokenizer, 
        max_length=5, 
        repetition_penalty=1.2
    )

def test_repetition_penalty_logic():
    """Test that repetition penalty reduces probability of repeated tokens."""
    vocab_size = 10
    model = MockModel(vocab_size)
    
    # Override forward to return specific logits for testing
    # We want to test that if token 1 is already generated, its score is reduced
    
    def manual_forward(input_ids, **kwargs):
        batch_size, seq_len = input_ids.shape
        # Create logits where token 1 has high score
        logits = torch.zeros(batch_size, seq_len, vocab_size)
        logits[:, :, 1] = 2.0  # High positive score
        logits[:, :, 2] = -2.0 # Negative score to test negative penalty logic
        return logits
    
    model.forward = manual_forward
    
    # 1. Test without penalty
    # Input is [1], next token logits should favour 1 (score 2.0)
    input_ids = torch.tensor([[1]])
    
    # We inspect the logic inside generate by mocking forward, but generate calls forward internally.
    # To verify the PENALTY application, we can't easily inspect the internal logits variable 
    # without adding print statements or using a debugger.
    # However, we can infer it from the output if we construct a case where penalty changes the winner.
    
    # Let's construct a case:
    # Token A has score 10.0
    # Token B has score 9.0
    # If we have generated Token A, and apply penalty 2.0:
    # Token A score becomes 10.0 / 2.0 = 5.0
    # Token B score remains 9.0
    # Token B should win (greedy)
    
    def specific_forward(input_ids, **kwargs):
        batch_size, seq_len = input_ids.shape
        logits = torch.zeros(batch_size, seq_len, vocab_size)
        logits[:, :, 1] = 10.0 # Token 1
        logits[:, :, 2] = 9.0  # Token 2
        return logits
    
    model.forward = specific_forward
    tokenizer = MagicMock()
    tokenizer.decode.side_effect = lambda x, **kwargs: str(x)
    
    # Case 1: No penalty. Token 1 should win.
    # Input is [1], preventing it from being empty. 
    # We want the model to generate one more token.
    # Greedy generation.
    input_tensor = torch.tensor([[1]])
    
    output_no_penalty = model.generate_greedy(
        input_tensor,
        max_length=1, # Generate 1 new token
        repetition_penalty=1.0
    )
    # The output includes the input. So shape is (1, 2)
    # The second token should be 1 (score 10 > 9)
    assert output_no_penalty[0, 1].item() == 1
    
    # Case 2: With penalty. Token 1 is in input. 
    # Penalty 2.0 -> Token 1 score 5.0, Token 2 score 9.0 -> Token 2 wins.
    output_with_penalty = model.generate_greedy(
        input_tensor,
        max_length=1,
        repetition_penalty=2.0
    )
    assert output_with_penalty[0, 1].item() == 2

def test_negative_score_penalty():
    """Test penalty logic for negative scores (should be multiplied)."""
    vocab_size = 10
    model = MockModel(vocab_size)
    
    # Case:
    # Token 1 score -5.0
    # Token 2 score -10.0
    # Token 1 wins normally (-5 > -10).
    # If Token 1 is in input, and penalty is 2.0:
    # Token 1 score becomes -5.0 * 2.0 = -10.0.
    # Token 2 score remains -10.0.
    # Ties? Let's make Token 2 slightly better to avoid ties.
    # Token 2 score -9.0
    # Normal: -5 > -9 -> Token 1 wins.
    # Penalty: -10 < -9 -> Token 2 wins.
    
    def negative_forward(input_ids, **kwargs):
        batch_size, seq_len = input_ids.shape
        logits = torch.zeros(batch_size, seq_len, vocab_size)
        logits[:, :, 1] = -5.0
        logits[:, :, 2] = -9.0
        # Set others very low
        logits[:, :, 3:] = -100.0
        logits[:, :, 0] = -100.0
        return logits
        
    model.forward = negative_forward
    
    input_tensor = torch.tensor([[1]])
    
    # With penalty 2.0
    output = model.generate_greedy(
        input_tensor,
        max_length=1,
        repetition_penalty=2.0
    )
    # Should pick token 2
    assert output[0, 1].item() == 2
