"""
Nonfiction reading passage evaluator for educational content.

This module provides an evaluator for nonfiction reading passages, assessing them
across quality dimensions including factual accuracy, reading level, and question quality.
"""

import logging
from pathlib import Path
from typing import List, Optional

from inceptbench_new.evaluators.base import BaseEvaluator
from inceptbench_new.models import BaseEvaluationResult, ReadingEvaluationResult

logger = logging.getLogger(__name__)


class NonfictionReadingEvaluator(BaseEvaluator):
    """
    Evaluator for nonfiction reading passages.
    
    Assesses passages across 9 metrics:
    - overall (continuous [0.0, 1.0])
    - factual_accuracy (binary - factual correctness)
    - educational_accuracy (binary)
    - reading_level_match (binary)
    - length_appropriateness (binary)
    - topic_focus (binary)
    - engagement (binary)
    - accuracy_and_logic (binary)
    - question_quality (binary)
    """
    
    def _load_prompt(self) -> str:
        """Load the nonfiction reading evaluation prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "nonfiction_reading" / "evaluation.txt"
        return self._load_prompt_from_file(prompt_path)
    
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """Return the ReadingEvaluationResult model."""
        return ReadingEvaluationResult
    
    async def evaluate(
        self,
        content: str,
        curriculum: str = "common_core",
        full_context: Optional[str] = None,
        subcontent_results: Optional[List[BaseEvaluationResult]] = None,
        generation_prompt: Optional[str] = None
    ) -> ReadingEvaluationResult:
        """
        Evaluate a nonfiction reading passage across all quality dimensions.
        
        Uses the default evaluation flow from BaseEvaluator, then sets the
        specific content_type for nonfiction reading.
        
        Args:
            content: The nonfiction passage content to evaluate
            curriculum: Curriculum to use for evaluation (default: "common_core")
            full_context: Complete root content for contextual evaluation (optional)
            subcontent_results: Results from evaluating nested content (optional)
            generation_prompt: Optional generation prompt used to create the content (optional)
            
        Returns:
            ReadingEvaluationResult with scores and rationales for all metrics
            
        Raises:
            RuntimeError: If evaluation fails
        """
        # Call default evaluation with all parameters
        result = await super().evaluate(content, curriculum, full_context, subcontent_results, generation_prompt)
        
        # Set content type specifically for nonfiction reading
        result.content_type = "nonfiction_reading"
        
        return result

