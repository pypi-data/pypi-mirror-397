"""
Base evaluator class for educational content evaluation.

This module defines the abstract base class that all content-type-specific
evaluators must extend.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional

from inceptbench_new.config import settings
from inceptbench_new.models import BaseEvaluationResult
from inceptbench_new.tools.api_client import get_async_openai_client
from inceptbench_new.tools.curriculum_search import get_curriculum_context
from inceptbench_new.tools.image_utils import extract_image_urls, prepare_images_for_api
from inceptbench_new.tools.object_counter import count_objects_in_images, format_count_data_for_prompt

logger = logging.getLogger(__name__)


class BaseEvaluator(ABC):
    """
    Abstract base class for all content evaluators.
    
    Provides common functionality for:
    - Loading prompts from files
    - Getting curriculum context
    - Getting object count context for images
    - Structuring evaluation calls
    
    Subclasses must implement:
    - _load_prompt(): Load evaluator-specific prompt
    - evaluate(): Perform the evaluation
    - _get_result_model(): Return the Pydantic model for results
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize the evaluator.
        
        Args:
            model: Model to use for evaluation (defaults to settings.EVALUATION_MODEL)
        """
        self.model = model or settings.EVALUATION_MODEL
        self.prompt_template = self._load_prompt()
        
    @abstractmethod
    def _load_prompt(self) -> str:
        """
        Load the evaluator-specific prompt from file.
        
        Returns:
            Prompt template string
            
        Raises:
            RuntimeError: If prompt file cannot be loaded
        """
        pass
    
    async def evaluate(
        self, 
        content: str, 
        curriculum: str = "common_core",
        full_context: Optional[str] = None,
        subcontent_results: Optional[List[BaseEvaluationResult]] = None,
        generation_prompt: Optional[str] = None
    ) -> BaseEvaluationResult:
        """
        Evaluate the content and return structured results.
        
        This is the default implementation that handles the common evaluation flow:
        1. Get programmatic analysis context (if any)
        2. Get curriculum context
        3. Get object count context
        4. Add generation_prompt context if provided (for AI-generated content)
        5. Add full_context if provided (for hierarchical content)
        6. Add subcontent_results if provided (for parent content)
        7. Build system prompt with all contexts
        8. Call LLM evaluator
        9. Return results
        
        Subclasses can override this method for custom behavior, or just override
        _get_programmatic_context() to add custom analyses.
        
        Args:
            content: The educational content to evaluate (specific node content)
            curriculum: Curriculum to use for evaluation (default: "common_core")
            full_context: Complete root content for contextual evaluation (optional)
            subcontent_results: Results from evaluating nested content (optional)
            generation_prompt: Prompt used to generate the content (optional, for AI-generated content)
            
        Returns:
            Evaluation results specific to the content type
            
        Raises:
            RuntimeError: If evaluation fails
        """
        start_time = time.time()
        content_type_name = self._get_result_model().__name__.replace("EvaluationResult", "").lower()
        logger.info(f"Evaluating {content_type_name}...")
        
        try:
            # Gather context in parallel (no dependencies between these calls)
            programmatic_context, curriculum_context, object_count_context = await asyncio.gather(
                self._get_programmatic_context(content),
                self._get_curriculum_context(content, curriculum),
                self._get_object_count_context(content)
            )

            # Get generation prompt context if provided (sync, no IO)
            generation_prompt_context = self._format_generation_prompt_context(generation_prompt)
            
            # Build complete system prompt (contexts are prepended to prompt template)
            system_prompt = self.prompt_template
            
            # Add hierarchical context (if provided)
            if full_context and full_context != content:
                context_note = (
                    "\n\n## FULL CONTEXT\n\n"
                    "This content is part of a larger educational resource. "
                    "The complete context is provided below for reference:\n\n"
                    f"{full_context}\n\n"
                    "---\n\n"
                    "You are evaluating the SPECIFIC content provided in the user message, "
                    "but you should consider how it relates to and fits within the full context above."
                )
                system_prompt = context_note + "\n\n" + system_prompt
            
            # Add subcontent evaluation results (if provided)
            if subcontent_results:
                subcontent_context = self._format_subcontent_results(subcontent_results)
                system_prompt = subcontent_context + "\n\n" + system_prompt
            
            # Add standard contexts
            if programmatic_context:
                system_prompt = programmatic_context + "\n\n" + system_prompt
            if object_count_context:
                system_prompt = object_count_context + "\n\n" + system_prompt
            if curriculum_context:
                system_prompt = curriculum_context + "\n\n" + system_prompt
            if generation_prompt_context:
                system_prompt = generation_prompt_context + "\n\n" + system_prompt
            
            # Call LLM evaluator
            result_model = self._get_result_model()
            result = await self._call_llm_evaluator(
                content=content,
                system_prompt=system_prompt,
                result_model=result_model
            )
            
            logger.info(
                f"{content_type_name.capitalize()} evaluation complete in {time.time() - start_time:.2f}s. "
                f"Overall: {result.overall.score:.2f}"
            )
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating {content_type_name}: {e}")
            raise RuntimeError(f"{content_type_name.capitalize()} evaluation failed: {e}")
    
    @abstractmethod
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """
        Return the Pydantic model class for this evaluator's results.
        
        Returns:
            Pydantic model class (e.g., QuestionEvaluationResult)
        """
        pass
    
    async def _get_programmatic_context(self, content: str) -> str:
        """
        Hook for subclasses to add programmatic analysis context.
        
        Override this method to perform programmatic analyses (e.g., chi-square
        test for answer balance in quizzes) and return formatted context to
        prepend to the system prompt.
        
        Args:
            content: The educational content
            
        Returns:
            Formatted programmatic analysis context string (empty by default)
        """
        return ""
    
    def _format_subcontent_results(self, subcontent_results: List[BaseEvaluationResult]) -> str:
        """
        Format subcontent evaluation results for inclusion in parent evaluation prompt.
        
        This provides the parent evaluator with context about how its nested
        components were evaluated.
        
        Args:
            subcontent_results: List of evaluation results from subcontent
            
        Returns:
            Formatted string describing subcontent evaluations
        """
        if not subcontent_results:
            return ""
        
        lines = [
            "\n\n## NESTED CONTENT EVALUATIONS\n",
            f"This content contains {len(subcontent_results)} nested component(s) that have been evaluated.",
            "Consider how these component evaluations relate to the overall quality:\n"
        ]
        
        for i, subcontent_result in enumerate(subcontent_results, 1):
            content_type = subcontent_result.content_type
            overall_score = subcontent_result.overall.score
            
            lines.append(f"\n### Component {i}: {content_type}")
            lines.append(f"- Overall Score: {overall_score:.2f}")
            lines.append(f"- Factual Accuracy: {subcontent_result.factual_accuracy.score:.1f}")
            lines.append(f"- Educational Accuracy: {subcontent_result.educational_accuracy.score:.1f}")
            
            # Add key insights from overall reasoning (first sentence)
            reasoning_preview = subcontent_result.overall.reasoning.split('.')[0] + "."
            lines.append(f"- Summary: {reasoning_preview}")
            
            # If subcontent has suggestions, note them
            if subcontent_result.overall.suggested_improvements:
                improvements_preview = subcontent_result.overall.suggested_improvements.split('.')[0] + "."
                lines.append(f"- Key Improvement: {improvements_preview}")
        
        lines.append(
            "\n**Use this information** to assess whether the nested components work well together "
            "and support the overall educational goals. Consider coherence, progression, and "
            "whether the components complement each other effectively."
        )
        
        return "\n".join(lines)
    
    async def _get_curriculum_context(self, content: str, curriculum: str) -> str:
        """
        Get curriculum context for the content.
        
        Extracts explicit curriculum standards if present, or searches
        based on content. Returns formatted context string.
        
        Args:
            content: The educational content
            curriculum: Curriculum name
            
        Returns:
            Formatted curriculum context string (may be empty)
        """
        try:
            return await get_curriculum_context(content, curriculum)
        except Exception as e:
            logger.warning(f"Error getting curriculum context: {e}")
            return ""
    
    async def _get_object_count_context(self, content: str) -> str:
        """
        Get object count context if images are present in the content.
        
        Extracts image URLs, counts objects in images, and returns
        formatted context string.
        
        Args:
            content: The educational content
            
        Returns:
            Formatted object count context string (may be empty)
        """
        try:
            image_urls = extract_image_urls(content)
            if not image_urls:
                return ""
            
            logger.info(f"Found {len(image_urls)} image(s) in content, counting objects...")
            count_result = await count_objects_in_images(image_urls)
            object_count_context = format_count_data_for_prompt(count_result)
            logger.info("Object count context generated")
            return object_count_context
            
        except Exception as e:
            logger.warning(f"Error getting object count context: {e}")
            return ""
    
    def _format_generation_prompt_context(self, generation_prompt: Optional[str]) -> str:
        """
        Format the generation prompt context for inclusion in the system prompt.
        
        The generation prompt represents the instructions used to create AI-generated
        content. When present, it helps the evaluator understand the intended purpose
        and goals of the content, which is especially relevant for metrics like
        educational_accuracy and curriculum_alignment.
        
        Args:
            generation_prompt: The prompt used to generate the content (optional)
            
        Returns:
            Formatted generation prompt context string (empty if no prompt provided)
        """
        if not generation_prompt or not generation_prompt.strip():
            return ""
        
        return (
            "## GENERATION PROMPT\n\n"
            "The content you are evaluating was AI-generated using the following prompt. "
            "Use this prompt as an expression of the intended purpose, goals, and requirements "
            "for the content. When assessing metrics such as educational_accuracy, "
            "curriculum_alignment, or any other metrics where understanding the intended "
            "purpose is relevant, consider whether the content successfully fulfills the "
            "requirements expressed in this generation prompt:\n\n"
            f"{generation_prompt.strip()}\n\n"
            "---"
        )
    
    def _load_prompt_from_file(self, prompt_file_path: Path) -> str:
        """
        Helper method to load prompt from a file path.
        
        Args:
            prompt_file_path: Path to the prompt file
            
        Returns:
            Prompt content as string
            
        Raises:
            RuntimeError: If file cannot be loaded
        """
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error loading prompt from {prompt_file_path}: {e}")
            raise RuntimeError(f"Could not load prompt: {e}")
    
    async def _call_llm_evaluator(
        self,
        content: str,
        system_prompt: str,
        result_model: type[BaseEvaluationResult]
    ) -> BaseEvaluationResult:
        """
        Helper method to call LLM for evaluation with structured output.
        
        Args:
            content: The content to evaluate
            system_prompt: The complete system prompt (including context)
            result_model: Pydantic model for structured output
            
        Returns:
            Evaluation result
            
        Raises:
            RuntimeError: If LLM call fails
        """
        try:
            client = get_async_openai_client(timeout=settings.DEFAULT_TIMEOUT)
            
            # Build user content with images if present
            user_content = [
                {"type": "input_text", "text": f"Please evaluate this content:\n\n{content}"}
            ]
            
            # Add images if present
            image_urls = extract_image_urls(content)
            if image_urls:
                logger.info(f"Adding {len(image_urls)} image(s) to evaluation")
                image_content = prepare_images_for_api(image_urls)
                user_content.extend(image_content)
            
            # Call LLM with structured output
            response = await client.responses.parse(
                model=self.model,
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                text_format=result_model
            )
            
            # Extract the evaluation from the structured response
            for output_item in response.output:
                if output_item.type == "message":
                    for content_item in output_item.content:
                        if (content_item.type == "output_text" and 
                            hasattr(content_item, "parsed") and 
                            content_item.parsed is not None):
                            return content_item.parsed
            
            # Fallback if parsing fails
            raise RuntimeError("Could not parse evaluation results from LLM response")
            
        except Exception as e:
            logger.error(f"Error calling LLM evaluator: {e}")
            raise RuntimeError(f"Evaluation failed: {e}")

