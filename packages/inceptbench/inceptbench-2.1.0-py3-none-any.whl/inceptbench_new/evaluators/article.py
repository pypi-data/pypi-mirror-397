"""
Article evaluator.

This module provides evaluation for educational articles - instructional content
designed to teach concepts through direct instruction, worked examples, and
practice problems.
"""

import logging
from pathlib import Path

from inceptbench_new.models.article import ArticleEvaluationResult
from inceptbench_new.models.base import BaseEvaluationResult

from .base import BaseEvaluator

logger = logging.getLogger(__name__)


class ArticleEvaluator(BaseEvaluator):
    """
    Evaluator for educational articles.
    
    Articles are instructional content that teach concepts through:
    - Direct instruction and explanations
    - Worked examples demonstrating processes
    - Practice problems for student application
    
    This evaluator assesses:
    - Overall instructional quality
    - Factual accuracy of content
    - Educational accuracy (fulfills learning intent)
    - Curriculum alignment
    - Teaching quality and pedagogical approach
    - Quality of worked examples
    - Quality of practice problems
    - Adherence to direct instruction principles
    - Quality of visual stimuli (images, diagrams)
    - Appropriateness of language and sentence structure
    """
    
    def _load_prompt(self) -> str:
        """Load the article evaluation prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "article" / "evaluation.txt"
        return self._load_prompt_from_file(prompt_path)
    
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """Return the article evaluation result model."""
        return ArticleEvaluationResult

