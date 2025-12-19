"""Trainer: Unified training and instruction tuning utilities."""

# Data utilities
from .data.loader import create_dataloader, Batch
from .data.dataset import InstructionDataset
from .data.collate import (
    InstructionCollator,
    InstructionCollatorWithPromptMasking,
    InferenceCollator,
)
from .data.format import (
    FormatterRegistry,
    ChatMLFormatter,
    AlpacaFormatter,
)

# Training Engine
from .engine import BaseTrainer
from .trainers import (
    train,
    CausalLMTrainer,
    MaskedLMTrainer,
    Seq2SeqTrainer,
    CustomTrainer,
    MultiTaskTrainer,
)

# Instruction Tuning
from .instruct_engine import InstructTrainer
