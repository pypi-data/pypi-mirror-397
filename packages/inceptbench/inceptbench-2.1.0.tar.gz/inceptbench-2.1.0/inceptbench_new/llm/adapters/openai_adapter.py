"""
OpenAI adapter for the LLM abstraction layer.

This module provides an adapter for OpenAI models (GPT-4, GPT-5, etc.)
that implements the LLMInterface.
"""

import logging
from typing import List, Optional, Type, Union

from openai import AsyncOpenAI
from pydantic import BaseModel

from inceptbench_new.llm.base import LLMImage, LLMInterface, LLMMessage

logger = logging.getLogger(__name__)


class OpenAIAdapter(LLMInterface):
    """
    Adapter for OpenAI API (GPT models).
    
    This adapter handles all OpenAI-specific details:
    - Authentication and API client setup
    - Request/response format conversion
    - Structured output via responses.parse()
    - Vision input handling
    - Error handling and retries
    
    The adapter uses OpenAI's modern responses API, which provides
    better support for structured output and vision inputs.
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
        Initialize OpenAI adapter.
        
        Args:
            model: Model identifier (e.g., "gpt-5", "gpt-4")
            api_key: OpenAI API key
            timeout: Request timeout in seconds
            temperature: Sampling temperature (stored but not used by OpenAI API)
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            model=model,
            api_key=api_key,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            timeout=self.timeout
        )
        logger.debug(f"OpenAI adapter initialized: {self.model}")
    
    async def generate_text(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> str:
        """
        Generate plain text using OpenAI responses API.
        
        Note: Temperature is not supported by OpenAI's responses API.
        
        Args:
            messages: Conversation messages
            **kwargs: Override max_tokens, etc. (temperature not supported)
            
        Returns:
            Generated text string
        """
        # Convert our standard message format to OpenAI format
        input_messages = [msg.to_dict() for msg in messages]
        
        try:
            response = await self.client.responses.create(
                model=self.model,
                input=input_messages
                # Note: temperature parameter not supported by OpenAI responses API
            )
            
            # Extract text from response structure
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if content_item.type == "output_text":
                            return content_item.text.strip()
            
            raise ValueError("No text output found in OpenAI response")
            
        except Exception as e:
            logger.error(f"OpenAI text generation failed: {e}")
            raise
    
    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output using OpenAI responses.parse().
        
        This method uses OpenAI's native structured output support,
        which ensures the response conforms to the Pydantic schema.
        
        Note: Temperature is not supported by OpenAI's responses API.
        
        Args:
            messages: Conversation messages
            response_schema: Pydantic model class for output structure
            **kwargs: Override max_tokens, etc. (temperature not supported)
            
        Returns:
            Instance of response_schema with model output
        """
        # Convert our standard message format to OpenAI format
        input_messages = [msg.to_dict() for msg in messages]
        
        try:
            response = await self.client.responses.parse(
                model=self.model,
                input=input_messages,
                text_format=response_schema
                # Note: temperature parameter not supported by OpenAI responses API
            )
            
            # Extract parsed output from response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            return content_item.parsed
            
            raise ValueError("No structured output found in OpenAI response")
            
        except Exception as e:
            logger.error(
                f"OpenAI structured output generation failed for "
                f"{response_schema.__name__}: {e}"
            )
            raise
    
    async def generate_with_vision(
        self,
        messages: List[LLMMessage],
        images: List[LLMImage],
        response_schema: Optional[Type[BaseModel]] = None,
        **kwargs
    ) -> Union[str, BaseModel]:
        """
        Generate response with image inputs (GPT-4 Vision, GPT-5).
        
        Handles both plain text and structured output with vision.
        Images can be provided as URLs or base64-encoded data.
        
        Note: Temperature is not supported by OpenAI's responses API.
        
        Args:
            messages: Conversation messages
            images: List of images to analyze
            response_schema: Optional schema for structured output
            **kwargs: Override max_tokens, etc. (temperature not supported)
            
        Returns:
            Text string if no schema, otherwise instance of response_schema
        """
        if not self.supports_vision:
            raise NotImplementedError(
                f"Model {self.model} does not support vision inputs"
            )
        
        # Build content array for user message
        content = []
        
        # Add text from user messages
        for msg in messages:
            if msg.role == "user":
                content.append({"type": "input_text", "text": msg.content})
        
        # Add images
        for img in images:
            if img.url:
                content.append({
                    "type": "input_image",
                    "source": {"type": "url", "url": img.url}
                })
            elif img.base64_data:
                content.append({
                    "type": "input_image",
                    "source": {
                        "type": "base64",
                        "media_type": img.media_type,
                        "data": img.base64_data
                    }
                })
        
        # Build input messages with system message if present
        input_messages = []
        system_msg = next((msg for msg in messages if msg.role == "system"), None)
        if system_msg:
            input_messages.append({"role": "system", "content": system_msg.content})
        
        input_messages.append({"role": "user", "content": content})
        
        try:
            if response_schema:
                # Structured output with vision
                response = await self.client.responses.parse(
                    model=self.model,
                    input=input_messages,
                    text_format=response_schema
                    # Note: temperature parameter not supported by OpenAI responses API
                )
                
                for output_item in response.output:
                    if output_item.type == "message":
                        for content_item in output_item.content:
                            if (content_item.type == "output_text" and 
                                hasattr(content_item, "parsed") and 
                                content_item.parsed is not None):
                                return content_item.parsed
                
                raise ValueError("No structured output found in vision response")
            else:
                # Plain text with vision
                response = await self.client.responses.create(
                    model=self.model,
                    input=input_messages
                    # Note: temperature parameter not supported by OpenAI responses API
                )
                
                for output_item in response.output:
                    if output_item.type == "message":
                        for content_item in output_item.content:
                            if content_item.type == "output_text":
                                return content_item.text.strip()
                
                raise ValueError("No text output found in vision response")
                
        except Exception as e:
            logger.error(f"OpenAI vision generation failed: {e}")
            raise
    
    @property
    def supports_vision(self) -> bool:
        """Check if this model supports vision inputs."""
        # GPT-4 and GPT-5 models support vision
        model_lower = self.model.lower()
        return "gpt-4" in model_lower or "gpt-5" in model_lower
    
    @property
    def supports_structured_output(self) -> bool:
        """Check if this model supports native structured output."""
        # All modern OpenAI models support structured output via responses.parse()
        return True

