"""
Anthropic Claude adapter for the LLM abstraction layer.

This module provides an adapter for Anthropic's Claude models
that implements the LLMInterface.
"""

import logging
from typing import List, Optional, Type, Union

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from inceptbench_new.llm.base import LLMImage, LLMInterface, LLMMessage

logger = logging.getLogger(__name__)


class ClaudeAdapter(LLMInterface):
    """
    Adapter for Anthropic Claude API.
    
    This adapter handles all Claude-specific details:
    - Authentication and API client setup
    - Request/response format conversion
    - Structured output via tool calling
    - Vision input handling
    - Error handling and retries
    
    Claude uses a tool calling mechanism to generate structured output,
    which is abstracted away by this adapter.
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
        Initialize Claude adapter.
        
        Args:
            model: Model identifier (e.g., "claude-sonnet-4-5")
            api_key: Anthropic API key
            timeout: Request timeout in seconds
            temperature: Sampling temperature (0.0 = deterministic)
            max_tokens: Maximum tokens in response
        """
        super().__init__(
            model=model,
            api_key=api_key,
            timeout=timeout,
            temperature=temperature,
            max_tokens=max_tokens
        )
        self.client = AsyncAnthropic(
            api_key=self.api_key,
            timeout=self.timeout
        )
        logger.debug(f"Claude adapter initialized: {self.model}")
    
    def _prepare_messages(self, messages: List[LLMMessage]) -> tuple[Optional[str], list[dict]]:
        """
        Prepare messages for Claude API.
        
        Claude requires system messages to be separate from the messages array.
        
        Args:
            messages: Standard LLM messages
            
        Returns:
            Tuple of (system_content, user_messages)
        """
        # Extract system message if present
        system_content = next(
            (msg.content for msg in messages if msg.role == "system"),
            None
        )
        
        # Build user messages (Claude doesn't accept system in messages array)
        user_messages = [
            msg.to_dict()
            for msg in messages
            if msg.role != "system"
        ]
        
        return system_content, user_messages
    
    async def generate_text(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> str:
        """
        Generate plain text using Claude messages API.
        
        Args:
            messages: Conversation messages
            **kwargs: Override temperature, max_tokens, etc.
            
        Returns:
            Generated text string
        """
        system_content, user_messages = self._prepare_messages(messages)
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system_content,
                messages=user_messages,
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            # Extract text from response
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"Claude text generation failed: {e}")
            raise
    
    async def generate_structured(
        self,
        messages: List[LLMMessage],
        response_schema: Type[BaseModel],
        **kwargs
    ) -> BaseModel:
        """
        Generate structured output using Claude tool calling.
        
        Claude doesn't have native structured output, but we can use
        tool calling to achieve the same result. We define a tool with
        the schema as its input schema, and force Claude to use it.
        
        Args:
            messages: Conversation messages
            response_schema: Pydantic model class for output structure
            **kwargs: Override temperature, max_tokens, etc.
            
        Returns:
            Instance of response_schema with model output
        """
        system_content, user_messages = self._prepare_messages(messages)
        
        # Define tool from schema
        tool = {
            "name": "structured_output",
            "description": (
                f"Return structured output matching the {response_schema.__name__} schema"
            ),
            "input_schema": response_schema.model_json_schema()
        }
        
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system_content,
                messages=user_messages,
                tools=[tool],
                tool_choice={"type": "tool", "name": "structured_output"},
                temperature=kwargs.get("temperature", self.temperature)
            )
            
            # Extract tool use from response
            for content_block in response.content:
                if (content_block.type == "tool_use" and 
                    content_block.name == "structured_output"):
                    return response_schema(**content_block.input)
            
            raise ValueError("No structured output found in Claude response")
            
        except Exception as e:
            logger.error(
                f"Claude structured output generation failed for "
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
        Generate response with image inputs (Claude vision).
        
        Handles both plain text and structured output with vision.
        Images can be provided as URLs or base64-encoded data.
        
        Args:
            messages: Conversation messages
            images: List of images to analyze
            response_schema: Optional schema for structured output
            **kwargs: Override temperature, max_tokens, etc.
            
        Returns:
            Text string if no schema, otherwise instance of response_schema
        """
        if not self.supports_vision:
            raise NotImplementedError(
                f"Model {self.model} does not support vision inputs"
            )
        
        system_content, user_messages_base = self._prepare_messages(messages)
        
        # Build content array with text and images
        content = []
        
        # Add text from user messages
        for msg in messages:
            if msg.role == "user":
                content.append({"type": "text", "text": msg.content})
        
        # Add images to content
        for img in images:
            if img.url:
                # Note: Claude API expects base64 for images, but we'll pass URL
                # and let the adapter handle downloading if needed
                content.append({
                    "type": "image",
                    "source": {"type": "url", "url": img.url}
                })
            elif img.base64_data:
                content.append({
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": img.media_type,
                        "data": img.base64_data
                    }
                })
        
        # Build user messages with combined content
        user_messages = [{"role": "user", "content": content}]
        
        try:
            if response_schema:
                # Structured output with vision using tool calling
                tool = {
                    "name": "structured_output",
                    "description": (
                        f"Return structured output matching the {response_schema.__name__} schema"
                    ),
                    "input_schema": response_schema.model_json_schema()
                }
                
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    system=system_content,
                    messages=user_messages,
                    tools=[tool],
                    tool_choice={"type": "tool", "name": "structured_output"},
                    temperature=kwargs.get("temperature", self.temperature)
                )
                
                for content_block in response.content:
                    if (content_block.type == "tool_use" and 
                        content_block.name == "structured_output"):
                        return response_schema(**content_block.input)
                
                raise ValueError("No structured output found in vision response")
            else:
                # Plain text with vision
                response = await self.client.messages.create(
                    model=self.model,
                    max_tokens=kwargs.get("max_tokens", self.max_tokens),
                    system=system_content,
                    messages=user_messages,
                    temperature=kwargs.get("temperature", self.temperature)
                )
                
                return response.content[0].text.strip()
                
        except Exception as e:
            logger.error(f"Claude vision generation failed: {e}")
            raise
    
    @property
    def supports_vision(self) -> bool:
        """Check if this model supports vision inputs."""
        # Most Claude models support vision
        return "claude" in self.model.lower()
    
    @property
    def supports_structured_output(self) -> bool:
        """Check if this model supports native structured output."""
        # Claude uses tool calling for structured output
        return True

