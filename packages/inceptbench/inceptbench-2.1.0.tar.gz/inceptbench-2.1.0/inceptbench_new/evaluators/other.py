"""
Other content evaluator for educational materials.

This module provides an evaluator for general educational content that doesn't
fit into specific categories (questions, quizzes, reading passages).
"""

import logging
from pathlib import Path

from inceptbench_new.evaluators.base import BaseEvaluator
from inceptbench_new.models import BaseEvaluationResult, OtherEvaluationResult

logger = logging.getLogger(__name__)


class OtherEvaluator(BaseEvaluator):
    """
    Evaluator for general educational content.
    
    Assesses content across 8 metrics:
    - overall (continuous [0.0, 1.0])
    - factual_accuracy (binary)
    - educational_accuracy (binary)
    - educational_value (binary)
    - direct_instruction_alignment (binary)
    - content_appropriateness (binary)
    - clarity_and_organization (binary)
    - engagement (binary)
    """
    
    def _load_prompt(self) -> str:
        """Load the other content evaluation prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "other" / "evaluation.txt"
        return self._load_prompt_from_file(prompt_path)
    
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """Return the OtherEvaluationResult model."""
        return OtherEvaluationResult

