import torch
import torch.nn as nn
import torch.nn.functional as F

class KeyValueMemory(nn.Module):
    """
    A differentiable Key-Value memory store.
    
    Think of this as a dynamically updatable database "beside" the weights.
    Structure:
    - Keys: Vectors representing "what" the info is about (indexing).
    - Values: Vectors representing the actual info content.
    """
    def __init__(self, key_dim, value_dim, memory_size=1024):
        super().__init__()
        self.key_dim = key_dim
        self.value_dim = value_dim
        self.memory_size = memory_size
        
        # We store keys and values as buffers, not parameters, so they don't get updated by SGD 
        # unless specifically desired. They are "updated" by explicit "write" operations.
        # Initialize with zeros or small random values
        self.register_buffer("keys", torch.zeros(memory_size, key_dim))
        self.register_buffer("values", torch.zeros(memory_size, value_dim))
        self.register_buffer("usage", torch.zeros(memory_size)) # To track next empty slot

    def write(self, keys, values):
        """
        Write new facts into the memory.
        Args:
            keys: (batch_size, key_dim) - Embedding of the prompt/context
            values: (batch_size, value_dim) - Embedding of the answer/fact
        """
        batch_size = keys.size(0)
        
        # Simple FIFO or First-Empty logic for this demo
        # Find first empty slots (usage == 0)
        # Note: In a real distributed system this is complex, here we just overwrite for simplicity
        # if the memory is full or just use a circular buffer pointer.
        
        # For this demo, let's just cycle through entries (Circular Buffer)
        if not hasattr(self, 'write_pointer'):
            self.write_pointer = 0
            
        for i in range(batch_size):
            idx = (self.write_pointer + i) % self.memory_size
            self.keys[idx] = keys[i].detach() # Store detached to stop gradients back to encoder during write
            self.values[idx] = values[i].detach()
        
        self.write_pointer = (self.write_pointer + batch_size) % self.memory_size

    def read(self, query, k=1):
        """
        Retrieve from memory using Dot-Product Attention.
        Args:
            query: (batch_size, key_dim)
            k: number of top matches to retrieve (not used in soft attention, but useful for hard retrieval)
        
        Returns:
            retrieved_values: (batch_size, value_dim) weighted sum of relevant memories
        """
        # Similarity: (batch_size, memory_size)
        scores = torch.matmul(query, self.keys.t())
        
        # Softmax to get attention weights
        weights = F.softmax(scores, dim=-1) # (batch_size, memory_size)
        
        # Weighted sum of values
        # (batch_size, memory_size) x (memory_size, value_dim) -> (batch_size, value_dim)
        output = torch.matmul(weights, self.values)
        
        return output, weights

class RetrievalBlock(nn.Module):
    """
    A Transformer Block that includes a request to External Memory.
    
    Standard Block: Input -> SelfAttn -> FF -> Output
    Retrieval Block: Input -> SelfAttn -> CrossAttn(Memory) -> FF -> Output
    """
    def __init__(self, hidden_dim, memory_component):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.memory = memory_component
        
        # Queries come from the hidden state
        self.query_proj = nn.Linear(hidden_dim, memory_component.key_dim)
        
        # Gate to decide how much to trust memory vs internal belief
        self.gate = nn.Linear(hidden_dim + memory_component.value_dim, hidden_dim)
        self.layer_norm = nn.LayerNorm(hidden_dim)

    def forward(self, hidden_states):
        """
        Args:
            hidden_states: (batch_size, seq_len, hidden_dim)
        """
        # 1. Generate Queries from current thought (hidden states)
        # We usually only query for the last token in generation, or all tokens during training.
        queries = self.query_proj(hidden_states) # (batch, seq, key_dim)
        
        # 2. Flatten for batch processing if needed, or loop. 
        # Matmul handles (batch, seq, key_dim) x (key_dim, memory_size) broadcast fine usually.
        # But our memory.read expects 2D query (batch, key_dim). Let's adapt memory read or reshape here.
        
        # Let's perform read manually here to support sequence dimension
        # Similarity: (batch, seq, key_dim) @ (key_dim, memory_size) -> (batch, seq, memory_size)
        scores = torch.matmul(queries, self.memory.keys.t())
        weights = F.softmax(scores, dim=-1)
        
        # Retrieved: (batch, seq, memory_size) @ (memory_size, value_dim) -> (batch, seq, value_dim)
        retrieved_content = torch.matmul(weights, self.memory.values)
        
        # 3. Fuse Memory into Main Stream
        # Concat original thought + retrieved fact
        combined = torch.cat([hidden_states, retrieved_content], dim=-1)
        
        # Gating/Integration
        update = self.gate(combined) # Project back to hidden_dim
        
        # Residual connection
        output = self.layer_norm(hidden_states + update)
        
        return output

class MemoryHead(nn.Module):
    """
    prediction head for Self-Modifying Memory.
    
    Decides: 
    1. WHETHER to write (Gate)
    2. WHAT to address (Key)
    3. WHAT content to write (Value)
    """
    def __init__(self, hidden_dim, key_dim, value_dim):
        super().__init__()
        # Gate: 0 to 1. >0.5 means write.
        self.write_gate = nn.Linear(hidden_dim, 1)
        
        # What key to write to?
        self.write_key = nn.Linear(hidden_dim, key_dim)
        
        # What content to write?
        self.write_value = nn.Linear(hidden_dim, value_dim)
        
    def forward(self, hidden_state):
        # hidden_state: (batch, hidden_dim) - usually the last token's state
        
        gate_logit = self.write_gate(hidden_state)
        gate = torch.sigmoid(gate_logit)
        
        key = self.write_key(hidden_state)
        value = self.write_value(hidden_state)
        
        return gate, key, value
