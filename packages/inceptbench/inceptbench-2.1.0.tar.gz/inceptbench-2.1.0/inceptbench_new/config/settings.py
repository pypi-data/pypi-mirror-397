"""
Configuration settings for the Educational Content Evaluator.

This module manages environment variables, API keys, model configurations,
and other system-wide settings.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file in project root
# Look for .env in the parent directory of src/
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Application settings and configuration."""
    
    # API Keys (loaded from .env file)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    INCEPT_API_KEY: Optional[str] = os.getenv("INCEPT_API_KEY")
    
    # Model Configuration
    DEFAULT_MODEL: str = "gpt-5"
    CLASSIFIER_MODEL: str = "gpt-5"
    EVALUATION_MODEL: str = "gpt-5"
    
    # Timeouts (in seconds)
    DEFAULT_TIMEOUT: float = 300.0
    CLASSIFIER_TIMEOUT: float = 60.0
    CURRICULUM_SEARCH_TIMEOUT: float = 60.0
    
    # Curriculum Configuration
    DEFAULT_CURRICULUM: str = "common_core"
    
    # InceptAPI Configuration
    INCEPTAPI_BASE_URL: str = os.getenv(
        "INCEPTAPI_BASE_URL", 
        "https://inceptapi.rp.devfactory.com/api"
    )
    
    @classmethod
    def validate_api_keys(cls) -> None:
        """
        Validate that required API keys are present.
        
        Raises:
            ValueError: If OpenAI API key is missing (required)
        """
        if not cls.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required"
            )


# Create singleton instance
settings = Settings()

