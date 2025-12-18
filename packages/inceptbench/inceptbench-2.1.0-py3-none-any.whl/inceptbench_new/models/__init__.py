"""
Data models for the educational content evaluation system.

This module provides Pydantic models for:
- Content types and evaluation requests
- Evaluation results and metrics
- Content tree structures (hierarchical content)
- Specific result types (question, quiz, reading, other)
"""

from .base import (
    BaseEvaluationResult,
    ContentType,
    EvaluationRequest,
    MetricResult,
)
from .content_tree import ContentNode, ContentTree, DecompositionResult, ExtractedContent
from .article import ArticleEvaluationResult
from .other import OtherEvaluationResult
from .question import QuestionEvaluationResult
from .quiz import QuizEvaluationResult
from .reading import ReadingEvaluationResult

__all__ = [
    # Base models
    "ContentType",
    "MetricResult",
    "BaseEvaluationResult",
    "EvaluationRequest",
    # Content tree models
    "ContentNode",
    "ContentTree",
    "DecompositionResult",
    "ExtractedContent",
    # Specific evaluation results
    "QuestionEvaluationResult",
    "QuizEvaluationResult",
    "ReadingEvaluationResult",
    "ArticleEvaluationResult",
    "OtherEvaluationResult",
]

