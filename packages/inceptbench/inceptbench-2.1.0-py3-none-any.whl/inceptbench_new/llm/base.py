"""
Base classes and interfaces for LLM abstraction layer.

This module defines the core abstractions that all LLM providers must implement,
providing a unified interface regardless of the underlying API.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Type, Union

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    """
    Standard message format for LLM conversations.
    
    Attributes:
        role: Message role - "system", "user", or "assistant"
        content: The message content (text)
    """
    role: str = Field(..., description="Message role: system, user, or assistant")
    content: str = Field(..., description="Message content")
    
    def to_dict(self) -> dict:
        """Convert to dictionary format."""
        return {"role": self.role, "content": self.content}


class LLMImage(BaseModel):
    """
    Image input for vision-enabled models.
    
    Provide either a URL or base64-encoded data.
    
    Attributes:
        url: Direct URL to the image
        base64_data: Base64-encoded image data
        media_type: MIME type (e.g., "image/png", "image/jpeg")
    """
    url: Optional[str] = Field(None, description="Image URL")
    base64_data: Optional[str] = Field(None, description="Base64-encoded image data")
    media_type: str = Field("image/png", description="Image MIME type")
    
    def __init__(self, **data):
        super().__init__(**data)
        if not self.url and not self.base64_data:
            raise ValueError("Either url or base64_data must be provided")


class LLMInterface(ABC):
    """
    Abstract interface for LLM providers.
    
    All providers (OpenAI, Anthropic, etc.) must implement this interface
    to provide a consistent API regardless of the underlying implementation.
    
    The interface abstracts away provider-specific details like:
    - Authentication and API keys
    - Request/response formats
    - Tool calling mechanisms
    - Image handling
    - Structured output generation
    
    Subclasses should encapsulate all provider-specific logic within
    their implementations, keeping the interface clean and simple.
    """
    
    def __init__(
        self,
        model: str,
        api_key: str,
        timeout: float = 60.0,
        temperature: float = 0.0,
        max_tokens: int = 16384
    ):
        """
        Initialize the LLM interface.
        
        Args:
            model: Model identifier (e.g., "gpt-5", "claude-sonnet-4-5")
            api_key: API key for the provider
            timeout: Request timeout in seconds
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response
        """
        self.model = model
        self.api_key = api_key
        self.timeout = timeout
        self.temperature = temperature
        self.max_tokens = max_tokens
    
    @abstractmethod
    async def generate_text(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> str:
        """
        Generate plain text response from the model.
        
        Args:
            messages: Conversation messages (system, user, etc.)
            **kwargs: Provider-specific parameter overrides
            
        Returns:
            Generated text string
            
        Raises:
            Exception: Provider-specific errors should be caught and
                      re-raised as standard exceptions
        """
        pass
    
    @abstractmethod
    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output matching a Pydantic schema.
        
        This method ensures the model returns output that conforms to
        the specified schema, using provider-specific mechanisms like
        structured output APIs or tool calling.
        
        Args:
            messages: Conversation messages
            response_schema: Pydantic model class defining the output structure
            **kwargs: Provider-specific parameter overrides
            
        Returns:
            Instance of response_schema populated with model output
            
        Raises:
            ValueError: If schema cannot be satisfied or parsing fails
            Exception: Provider-specific errors
        """
        pass
    
    @abstractmethod
    async def generate_with_vision(
        self,
        messages: List[LLMMessage],
        images: List[LLMImage],
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs
    ) -> Union[str, BaseModel]:
        """
        Generate response with image inputs (vision models).
        
        Args:
            messages: Conversation messages
            images: List of images to analyze
            response_schema: Optional schema for structured output
            **kwargs: Provider-specific parameter overrides
            
        Returns:
            Text string if no schema provided, otherwise instance of response_schema
            
        Raises:
            NotImplementedError: If model doesn't support vision
            ValueError: If images cannot be processed
            Exception: Provider-specific errors
        """
        pass
    
    @property
    @abstractmethod
    def supports_vision(self) -> bool:
        """
        Check if this model supports image inputs.
        
        Returns:
            True if model can process images, False otherwise
        """
        pass
    
    @property
    @abstractmethod
    def supports_structured_output(self) -> bool:
        """
        Check if this model supports native structured output.
        
        Returns:
            True if model has native structured output support
        """
        pass
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"{self.__class__.__name__}(model='{self.model}')"

