"""
Question evaluator for educational content.

This module provides an evaluator for single questions, assessing them across
multiple quality dimensions including curriculum alignment, clarity, misconception
detection, and more.
"""

import logging
from pathlib import Path

from inceptbench_new.evaluators.base import BaseEvaluator
from inceptbench_new.models import BaseEvaluationResult, QuestionEvaluationResult

logger = logging.getLogger(__name__)


class QuestionEvaluator(BaseEvaluator):
    """
    Evaluator for single educational questions.
    
    Assesses questions across 11 metrics:
    - overall (continuous [0.0, 1.0])
    - factual_accuracy (binary)
    - educational_accuracy (binary)
    - curriculum_alignment (binary)
    - clarity_precision (binary)
    - reveals_misconceptions (binary)
    - difficulty_alignment (binary)
    - passage_reference (binary)
    - distractor_quality (binary)
    - stimulus_quality (binary)
    - mastery_learning_alignment (binary)
    """
    
    def _load_prompt(self) -> str:
        """Load the question evaluation prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "question" / "evaluation.txt"
        return self._load_prompt_from_file(prompt_path)
    
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """Return the QuestionEvaluationResult model."""
        return QuestionEvaluationResult

