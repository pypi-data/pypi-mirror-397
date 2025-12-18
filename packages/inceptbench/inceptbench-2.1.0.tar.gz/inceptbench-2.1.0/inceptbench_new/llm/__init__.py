"""
LLM abstraction layer for unified model access.

This module provides a provider-agnostic interface for interacting with
different LLM providers (OpenAI, Anthropic, etc.) through a common API.

Usage:
    from llm import LLMFactory, LLMMessage
    
    # Create an LLM for a specific task
    llm = LLMFactory.create("classifier")
    
    # Generate structured output
    result = await llm.generate_structured(
        messages=[
            LLMMessage(role="system", content="You are a classifier..."),
            LLMMessage(role="user", content="Classify this content...")
        ],
        response_schema=ClassificationResult
    )
"""

from .base import LLMImage, LLMInterface, LLMMessage
from .config import LLMConfig, get_llm_config
from .factory import LLMFactory

__all__ = [
    "LLMFactory",
    "LLMInterface",
    "LLMMessage",
    "LLMImage",
    "LLMConfig",
    "get_llm_config",
]

