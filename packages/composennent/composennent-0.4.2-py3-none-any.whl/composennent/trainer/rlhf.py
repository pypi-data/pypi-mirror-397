import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from typing import Optional, List, Dict, Union, Callable, Any
from .engine import BaseTrainer, Batch

class DPODataset(Dataset):
    """Dataset for DPO training.
    
    Expects data samples to be dictionaries with:
    - prompt
    - chosen
    - rejected
    """
    def __init__(self, data: List[Dict[str, str]], tokenizer, max_length: int = 512):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Tokenize prompt + chosen
        chosen_text = item["prompt"] + item["chosen"]
        chosen_enc = self.tokenizer.encode(chosen_text)
        
        # Tokenize prompt + rejected
        rejected_text = item["prompt"] + item["rejected"]
        rejected_enc = self.tokenizer.encode(rejected_text)
        
        # Crop to max_length
        chosen_enc = chosen_enc[:self.max_length]
        rejected_enc = rejected_enc[:self.max_length]
        
        return {
            "chosen_input_ids": torch.tensor(chosen_enc, dtype=torch.long),
            "rejected_input_ids": torch.tensor(rejected_enc, dtype=torch.long),
            "prompt_text": item["prompt"] # For online usage if needed, or verification
        }

def dpo_collate_fn(batch_list, pad_token_id=0):
    # Dynamic padding for both chosen and rejected
    max_len_chosen = max(item["chosen_input_ids"].size(0) for item in batch_list)
    max_len_rejected = max(item["rejected_input_ids"].size(0) for item in batch_list)
    
    bs = len(batch_list)
    
    chosen_ids = torch.full((bs, max_len_chosen), pad_token_id, dtype=torch.long)
    chosen_mask = torch.zeros((bs, max_len_chosen), dtype=torch.long)
    
    rejected_ids = torch.full((bs, max_len_rejected), pad_token_id, dtype=torch.long)
    rejected_mask = torch.zeros((bs, max_len_rejected), dtype=torch.long)
    
    for i, item in enumerate(batch_list):
        # Chosen
        l_c = item["chosen_input_ids"].size(0)
        chosen_ids[i, :l_c] = item["chosen_input_ids"]
        chosen_mask[i, :l_c] = 1
        
        # Rejected
        l_r = item["rejected_input_ids"].size(0)
        rejected_ids[i, :l_r] = item["rejected_input_ids"]
        rejected_mask[i, :l_r] = 1
        
    return {
        "chosen_input_ids": chosen_ids,
        "chosen_attention_mask": chosen_mask,
        "rejected_input_ids": rejected_ids,
        "rejected_attention_mask": rejected_mask,
        "prompts": [item["prompt_text"] for item in batch_list]
    }

class DPOTrainer(BaseTrainer):
    """Trainer for Direct Preference Optimization (DPO).
    
    Supports both offline (static dataset) and online (dynamic generation) modes.
    
    Args:
        model: Policy model to be trained.
        ref_model: Reference model (frozen).
        beta: Temperature parameter for DPO loss.
        reward_fn: Optional callable for Online DPO. 
                   Signature: reward_fn(texts: List[str]) -> List[float]
    """
    def __init__(
        self,
        model: torch.nn.Module,
        ref_model: torch.nn.Module,
        tokenizer,
        beta: float = 0.1,
        reward_fn: Optional[Callable[[List[str]], List[float]]] = None,
        **kwargs
    ):
        super().__init__(model, tokenizer, **kwargs)
        self.ref_model = ref_model
        self.ref_model.to(self.device)
        self.ref_model.eval() # Reference model is always frozen
        
        self.beta = beta
        self.reward_fn = reward_fn
        self.is_online = reward_fn is not None

    def get_batch_logps(self, model, input_ids, attention_mask):
        """Compute log probabilities of the input sequence."""
        # Forward pass
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs if isinstance(outputs, torch.Tensor) else outputs["logits"]
        
        # Shift logits and labels for next-token prediction
        # shape: (B, L-1, V)
        logits = logits[:, :-1, :] 
        # shape: (B, L-1)
        labels = input_ids[:, 1:]
        
        # Compute log probabilities
        # log_softmax over vocab dimension
        log_probs = F.log_softmax(logits, dim=-1)
        
        # Gather log probs of the actual tokens
        # labels.unsqueeze(-1) -> (B, L-1, 1)
        # gather -> (B, L-1, 1) -> squeeze -> (B, L-1)
        per_token_logps = torch.gather(log_probs, -1, labels.unsqueeze(-1)).squeeze(-1)
        
        # Mask out padding tokens (we assume attention_mask aligns with input_ids)
        # mask needs to be shifted too: (B, L-1)
        mask = attention_mask[:, 1:].float()
        
        # Sum log probs over valid tokens
        return (per_token_logps * mask).sum(-1)

    def training_step(self, batch_data) -> float:
        # 1. Handle Online Mode (Dynamic Generation)
        if self.is_online:
            # In online mode, batch_data is expected to be just prompts
            # or we simplify and say it contains 'prompts' key from our collator
            prompts = batch_data.get("prompts", [])
            if not prompts:
                # If using raw DataLoader with list of strings
                if isinstance(batch_data, list) and isinstance(batch_data[0], str):
                    prompts = batch_data
                else: 
                     return 0.0 # Skip if no prompts found/understood
            
            # Generate 2 complete samples per prompt
            # NOTE: This is a simplified generation implementation.
            # In production, use efficient batch generation.
            generated_pairs = []
            flat_texts = []
            
            self.model.eval() # Eval for generation
            for p in prompts:
                # Generate A
                # Naive generation for demo purposes
                # Using model's generate if available, else manual
                # Assuming model has a 'generate' method (from standard transformers or wrapper)
                # If not, we might need to implement a simple greedy loop here.
                # For now, let's assume `generate` exists and returns text.
                
                # Mock generation if method missing (to prevent crash in initial impl)
                if hasattr(self.model, "generate"):
                     # We need to tokenize P first
                     p_ids = self.tokenizer.encode(p, return_tensors="pt").to(self.device)
                     out_a = self.model.generate(p_ids, max_new_tokens=20, do_sample=True)
                     out_b = self.model.generate(p_ids, max_new_tokens=20, do_sample=True)
                     # Decode
                     text_a = self.tokenizer.decode(out_a[0], skip_special_tokens=True)
                     text_b = self.tokenizer.decode(out_b[0], skip_special_tokens=True)
                else:
                    # Fallback for testing without generation capable model
                    text_a = p + " output A"
                    text_b = p + " output B"
                
                flat_texts.extend([text_a, text_b])
                generated_pairs.append((text_a, text_b))
            
            self.model.train() # Back to train
            
            # Score
            scores = self.reward_fn(flat_texts) # expect [sA1, sB1, sA2, sB2...]
            
            # Construct Chosen/Rejected Batch
            chosen_ids_list = []
            rejected_ids_list = []
            
            for i, (txt_a, txt_b) in enumerate(generated_pairs):
                score_a = scores[2*i]
                score_b = scores[2*i+1]
                
                if score_a > score_b:
                    chosen, rejected = txt_a, txt_b
                else:
                    chosen, rejected = txt_b, txt_a
                
                chosen_ids_list.append(torch.tensor(self.tokenizer.encode(chosen), dtype=torch.long))
                rejected_ids_list.append(torch.tensor(self.tokenizer.encode(rejected), dtype=torch.long))
            
            # Collate manually
            # We can re-use dpo_collate logic but we already have tensors
            # Simplification: just pad efficiently
            def pad_tensors(tensors, pad_val):
                max_l = max(t.size(0) for t in tensors)
                res = torch.full((len(tensors), max_l), pad_val, dtype=torch.long, device=self.device)
                mask = torch.zeros((len(tensors), max_l), dtype=torch.long, device=self.device)
                for i, t in enumerate(tensors):
                    l = t.size(0)
                    res[i, :l] = t.to(self.device)
                    mask[i, :l] = 1
                return res, mask
            
            c_ids, c_mask = pad_tensors(chosen_ids_list, self.pad_token_id)
            r_ids, r_mask = pad_tensors(rejected_ids_list, self.pad_token_id)
            
            batch_data = {
                "chosen_input_ids": c_ids,
                "chosen_attention_mask": c_mask,
                "rejected_input_ids": r_ids,
                "rejected_attention_mask": r_mask
            }

        # 2. Standard DPO Step (Offline or Online-prepared)
        # Move to device if they are not already (Online step moves them, static loader might not)
        chosen_input_ids = batch_data["chosen_input_ids"].to(self.device)
        chosen_attention_mask = batch_data["chosen_attention_mask"].to(self.device)
        rejected_input_ids = batch_data["rejected_input_ids"].to(self.device)
        rejected_attention_mask = batch_data["rejected_attention_mask"].to(self.device)
        
        self.optimizer.zero_grad()
        
        # Policy Logps
        policy_chosen_logps = self.get_batch_logps(self.model, chosen_input_ids, chosen_attention_mask)
        policy_rejected_logps = self.get_batch_logps(self.model, rejected_input_ids, rejected_attention_mask)
        
        # Reference Logps (No Grad)
        with torch.no_grad():
            ref_chosen_logps = self.get_batch_logps(self.ref_model, chosen_input_ids, chosen_attention_mask)
            ref_rejected_logps = self.get_batch_logps(self.ref_model, rejected_input_ids, rejected_attention_mask)
        
        # DPO Loss
        # pi_logratios = policy_chosen - policy_rejected
        # ref_logratios = ref_chosen - ref_rejected
        # logits = pi_logratios - ref_logratios
        
        policy_log_ratios = policy_chosen_logps - policy_rejected_logps
        ref_log_ratios = ref_chosen_logps - ref_rejected_logps
        
        logits = policy_log_ratios - ref_log_ratios
        
        # loss = -log(sigmoid(beta * logits))
        losses = -F.logsigmoid(self.beta * logits)
        loss = losses.mean()
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item()

    def compute_loss(self, model_output, batch):
        # Unused in DPO training_step override, but required by abstract base
        return torch.tensor(0.0)

    def train(self, data: Union[List[Dict], List[str]] = None, **kwargs):
        """Override train to handle DPO data setup."""
        if data is not None and not kwargs.get("dataloader"):
            # Check if online (List[str]) or offline (List[Dict])
            is_online_data = isinstance(data[0], str)
            
            if self.is_online and is_online_data:
                # Online: data is just prompts
                # For simplicity, we create a dummy "Dataset" that strictly yields the strings
                # And a collator that passes them through
                batch_size = kwargs.get("batch_size", 4)
                
                class PromptDataset(Dataset):
                    def __init__(s, p): s.prompts = p
                    def __len__(s): return len(s.prompts)
                    def __getitem__(s, i): return s.prompts[i]
                
                ds = PromptDataset(data)
                dl = DataLoader(ds, batch_size=batch_size, collate_fn=lambda x: {"prompts": x})
                kwargs["dataloader"] = dl
                
            elif not is_online_data:
                # Offline: data is dicts {prompt, chosen, rejected}
                tokenizer = self.tokenizer
                ds = DPODataset(data, tokenizer)
                dl = DataLoader(ds, batch_size=kwargs.get("batch_size", 4), collate_fn=lambda x: dpo_collate_fn(x, self.pad_token_id))
                kwargs["dataloader"] = dl
        
        return super().train(**kwargs)
