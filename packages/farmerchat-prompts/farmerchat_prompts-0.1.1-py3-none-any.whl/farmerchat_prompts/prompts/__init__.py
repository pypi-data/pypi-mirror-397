"""
Prompt templates organized by domain and provider
"""

# Crop Advisory
from .crop_advisory.openai import OPENAI_PROMPTS
from .crop_advisory.llama import LLAMA_PROMPTS

# Prompt Evals
from .prompt_evals.openai import OPENAI_PROMPT_EVALS_PROMPTS

__all__ = [
    "OPENAI_PROMPTS", 
    "LLAMA_PROMPTS",
    "OPENAI_PROMPT_EVALS_PROMPTS",
    "GEMMA_PROMPT_EVALS_PROMPTS"
]