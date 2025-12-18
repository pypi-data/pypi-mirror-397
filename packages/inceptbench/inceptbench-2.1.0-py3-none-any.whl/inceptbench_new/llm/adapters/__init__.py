"""
LLM provider adapters.

This package contains adapter implementations for different LLM providers.
Each adapter implements the LLMInterface and handles provider-specific logic.
"""

from .claude_adapter import ClaudeAdapter
from .openai_adapter import OpenAIAdapter

__all__ = ["OpenAIAdapter", "ClaudeAdapter"]

