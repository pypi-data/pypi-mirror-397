"""
API client management for educational content evaluator.

This module provides functions to get configured API clients for various services.
"""

import os
from typing import Optional

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from inceptbench_new.config import settings


def get_async_openai_client(timeout: Optional[float] = None) -> AsyncOpenAI:
    """
    Get a configured async OpenAI client.
    
    Args:
        timeout: Optional timeout in seconds (defaults to settings.DEFAULT_TIMEOUT)
        
    Returns:
        Configured AsyncOpenAI client
        
    Raises:
        ValueError: If OPENAI_API_KEY is not set
    """
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY must be set in .env file")
    
    timeout_value = timeout if timeout is not None else settings.DEFAULT_TIMEOUT
    
    return AsyncOpenAI(
        api_key=settings.OPENAI_API_KEY,
        timeout=timeout_value
    )


def get_async_anthropic_client(timeout: Optional[float] = None) -> AsyncAnthropic:
    """
    Get a configured async Anthropic (Claude) client.
    
    Args:
        timeout: Optional timeout in seconds (defaults to settings.DEFAULT_TIMEOUT)
        
    Returns:
        Configured AsyncAnthropic client
        
    Raises:
        ValueError: If ANTHROPIC_API_KEY is not set
    """
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY must be set in .env file")
    
    timeout_value = timeout if timeout is not None else settings.DEFAULT_TIMEOUT
    
    return AsyncAnthropic(
        api_key=api_key,
        timeout=timeout_value
    )

