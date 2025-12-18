"""
Content classifier for educational materials.

This module provides a classifier that uses LLM to determine the type of
educational content (question, quiz, reading passage, etc.).
"""

import logging
import time
from pathlib import Path

from pydantic import BaseModel

from inceptbench_new.llm import LLMFactory, LLMMessage
from inceptbench_new.models import ContentType

logger = logging.getLogger(__name__)


class ContentClassificationResult(BaseModel):
    """Result from content classification."""
    content_type: ContentType
    confidence: str  # high, medium, low
    explanation: str


class ContentClassifier:
    """
    Classifies educational content into predefined types.
    
    Uses LLM with structured output to classify content as question, quiz,
    fiction reading, nonfiction reading, or other.
    """
    
    def __init__(self):
        """Initialize the content classifier."""
        self.llm = LLMFactory.create("classifier")
        self.system_prompt = self._load_prompt()
        
    def _load_prompt(self) -> str:
        """Load the classifier prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "classifier.txt"
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading classifier prompt: {e}")
            raise RuntimeError(f"Could not load classifier prompt: {e}")
    
    async def classify(self, content: str) -> ContentType:
        """
        Classify the content type.
        
        Args:
            content: The educational content to classify
            
        Returns:
            ContentType enum value indicating the classified type
            
        Raises:
            RuntimeError: If classification fails
        """
        start_time = time.time()
        logger.info("Classifying content type...")
        
        try:
            result = await self.llm.generate_structured(
                messages=[
                    LLMMessage(role="system", content=self.system_prompt),
                    LLMMessage(role="user", content=content)
                ],
                response_schema=ContentClassificationResult
            )
            
            logger.info(
                f"Classification completed in {time.time() - start_time:.2f}s: "
                f"{result.content_type.value} (confidence: {result.confidence})"
            )
            logger.debug(f"Classification explanation: {result.explanation}")
            return result.content_type
            
        except Exception as e:
            logger.error(f"Error classifying content: {str(e)}")
            # Default to OTHER if classification fails
            logger.info(
                f"Classification failed after {time.time() - start_time:.2f}s, "
                f"defaulting to OTHER"
            )
            return ContentType.OTHER