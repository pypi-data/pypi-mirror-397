"""
Factory for creating LLM instances based on task configuration.

This module provides the LLMFactory class which creates appropriate
LLM instances based on the task registry configuration.
"""

import logging
import os
from typing import Optional

from inceptbench_new.llm.base import LLMInterface
from inceptbench_new.llm.config import LLMConfig, get_llm_config

logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM instances.
    
    This class handles:
    - Looking up the correct provider for a task
    - Loading API keys from environment
    - Instantiating the appropriate adapter
    - Applying configuration (timeout, temperature, etc.)
    
    Usage:
        llm = LLMFactory.create("classifier")
        result = await llm.generate_structured(messages, schema)
    """
    
    # Registry of available adapters
    # Populated lazily to avoid import cycles
    _adapters = {}
    _initialized = False
    
    @classmethod
    def _ensure_initialized(cls):
        """Lazy initialization of adapter registry."""
        if not cls._initialized:
            # Import adapters here to avoid circular imports
            from inceptbench_new.llm.adapters.openai_adapter import OpenAIAdapter
            from inceptbench_new.llm.adapters.claude_adapter import ClaudeAdapter
            
            cls._adapters = {
                "openai": OpenAIAdapter,
                "anthropic": ClaudeAdapter,
                # Future: "gemini": GeminiAdapter,
            }
            cls._initialized = True
            logger.debug(f"LLM adapters initialized: {list(cls._adapters.keys())}")
    
    @classmethod
    def create(
        cls, 
        task: str, 
        config_override: Optional[LLMConfig] = None
    ) -> LLMInterface:
        """
        Create an LLM instance for a specific task.
        
        This is the main entry point for getting an LLM. It:
        1. Looks up the task configuration
        2. Gets the appropriate API key
        3. Instantiates the correct adapter
        4. Returns a ready-to-use LLM instance
        
        Args:
            task: Task name from LLM_TASK_REGISTRY (e.g., "classifier")
            config_override: Optional config to override registry defaults
                           (useful for A/B testing different models)
            
        Returns:
            Configured LLM instance ready for use
            
        Raises:
            ValueError: If task is unknown or provider is not supported
            RuntimeError: If API key is not set in environment
            
        Examples:
            # Use default configuration
            llm = LLMFactory.create("classifier")
            
            # Override configuration for testing
            custom_config = LLMConfig(
                provider="anthropic",
                model="claude-sonnet-4-5",
                timeout=30.0
            )
            llm = LLMFactory.create("classifier", config_override=custom_config)
        """
        cls._ensure_initialized()
        
        # Get configuration (override or default)
        config = config_override or get_llm_config(task)
        
        logger.debug(
            f"Creating LLM for task '{task}': "
            f"{config.provider}/{config.model}"
        )
        
        # Validate provider
        if config.provider not in cls._adapters:
            raise ValueError(
                f"Unsupported provider: '{config.provider}'. "
                f"Available providers: {list(cls._adapters.keys())}"
            )
        
        # Get API key from environment
        api_key = cls._get_api_key(config.provider)
        
        # Instantiate the appropriate adapter
        adapter_class = cls._adapters[config.provider]
        llm = adapter_class(
            model=config.model,
            api_key=api_key,
            timeout=config.timeout,
            temperature=config.temperature,
            max_tokens=config.max_tokens
        )
        
        logger.info(
            f"Created {config.provider} LLM for '{task}': {config.model} "
            f"(timeout={config.timeout}s, temp={config.temperature})"
        )
        
        return llm
    
    @staticmethod
    def _get_api_key(provider: str) -> str:
        """
        Get API key for a provider from environment.
        
        Args:
            provider: Provider name (openai, anthropic, gemini)
            
        Returns:
            API key string
            
        Raises:
            RuntimeError: If API key environment variable is not set
        """
        # Map provider to environment variable name
        key_map = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "gemini": "GEMINI_API_KEY",
        }
        
        env_var = key_map.get(provider)
        if not env_var:
            raise ValueError(f"Unknown provider: {provider}")
        
        api_key = os.getenv(env_var)
        if not api_key:
            raise RuntimeError(
                f"{env_var} not set in environment. "
                f"Please add it to your .env file."
            )
        
        return api_key
    
    @classmethod
    def available_providers(cls) -> list[str]:
        """
        Get list of available providers.
        
        Returns:
            List of provider names
        """
        cls._ensure_initialized()
        return list(cls._adapters.keys())

