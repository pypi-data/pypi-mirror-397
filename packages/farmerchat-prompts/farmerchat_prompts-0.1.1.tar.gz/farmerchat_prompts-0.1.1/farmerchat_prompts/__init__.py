"""
FarmerChat Prompts - A prompt management library for agricultural AI applications
"""

from .manager import PromptManager
from .models import Prompt, PromptMetadata, Provider, UseCase, Domain

__version__ = "0.2.0"
__all__ = ["PromptManager", "Prompt", "PromptMetadata", "Provider", "UseCase", "Domain"]
