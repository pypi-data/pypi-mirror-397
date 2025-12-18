"""
Utility tools for the educational content evaluation system.

This module provides various utility functions including:
- API client management (legacy, prefer src.llm)
- Curriculum search functionality
- Object counting in images
- Image utilities
"""

# Note: API clients are legacy - prefer using src.llm.LLMFactory
from .api_client import get_async_anthropic_client, get_async_openai_client

__all__ = [
    "get_async_openai_client",
    "get_async_anthropic_client",
]

