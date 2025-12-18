"""
Data models for quiz evaluation.

This module defines the Pydantic models used for evaluating quizzes (sets of
multiple questions), including all metrics specific to quiz content.
"""

from pydantic import Field, field_validator

from .base import BaseEvaluationResult, MetricResult


class QuizEvaluationResult(BaseEvaluationResult):
    """
    Evaluation result for a quiz (set of multiple questions).
    
    Includes the required metrics (overall, factual_accuracy, educational_accuracy)
    plus quiz-specific metrics that assess overall quiz quality.
    
    All metrics except 'overall' are binary (0.0 or 1.0).
    """
    
    content_type: str = Field(default="quiz", description="Type of content (quiz)")
    
    # Quiz-specific metrics (all binary)
    concept_coverage: MetricResult = Field(
        ...,
        description="Whether quiz covers all major concepts comprehensively"
    )
    
    difficulty_distribution: MetricResult = Field(
        ...,
        description="Whether quiz has appropriate balance of difficulty levels"
    )
    
    non_repetitiveness: MetricResult = Field(
        ...,
        description="Whether quiz avoids redundant or repetitive questions"
    )
    
    test_preparedness: MetricResult = Field(
        ...,
        description="Whether quiz aligns with standardized test composition and format"
    )
    
    answer_balance: MetricResult = Field(
        ...,
        description="Whether correct answer positions are well-distributed (for MC questions)"
    )
    
    @field_validator(
        'concept_coverage',
        'difficulty_distribution',
        'non_repetitiveness',
        'test_preparedness',
        'answer_balance'
    )
    @classmethod
    def validate_binary_metrics(cls, v: MetricResult) -> MetricResult:
        """Ensure quiz-specific metrics are binary (0.0 or 1.0)."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Quiz metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v

