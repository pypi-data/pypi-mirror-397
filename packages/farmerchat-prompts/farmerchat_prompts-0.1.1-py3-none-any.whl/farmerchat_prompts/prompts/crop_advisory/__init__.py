"""Crop advisory prompts"""

from .openai import OPENAI_PROMPTS
from .llama import LLAMA_PROMPTS
from .gemma import GEMMA_PROMPTS

__all__ = ["OPENAI_PROMPTS", "LLAMA_PROMPTS", "GEMMA_PROMPTS"]