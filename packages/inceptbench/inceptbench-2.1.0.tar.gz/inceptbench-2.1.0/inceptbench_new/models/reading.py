"""
Data models for reading passage evaluation.

This module defines the Pydantic models used for evaluating reading passages
(both fiction and nonfiction), including all metrics specific to reading content.
"""

from pydantic import Field, field_validator

from .base import BaseEvaluationResult, MetricResult


class ReadingEvaluationResult(BaseEvaluationResult):
    """
    Evaluation result for a reading passage (fiction or nonfiction).
    
    Includes the required metrics (overall, factual_accuracy, educational_accuracy)
    plus reading-specific metrics that assess passage and question quality.
    
    All metrics except 'overall' are binary (0.0 or 1.0).
    """
    
    # content_type will be set to "fiction_reading" or "nonfiction_reading" by evaluator
    
    # Reading-specific metrics (all binary)
    reading_level_match: MetricResult = Field(
        ...,
        description="Whether passage aligns with expected Lexile range and grade level"
    )
    
    length_appropriateness: MetricResult = Field(
        ...,
        description="Whether passage length is appropriate for grade level and type"
    )
    
    topic_focus: MetricResult = Field(
        ...,
        description="Whether passage stays focused on topic without unnecessary tangents"
    )
    
    engagement: MetricResult = Field(
        ...,
        description="Whether passage is engaging and well-structured for target audience"
    )
    
    accuracy_and_logic: MetricResult = Field(
        ...,
        description="Whether passage is factually accurate (nonfiction) or logically consistent (fiction)"
    )
    
    question_quality: MetricResult = Field(
        ...,
        description="Quality of comprehension questions if present"
    )
    
    @field_validator(
        'reading_level_match',
        'length_appropriateness',
        'topic_focus',
        'engagement',
        'accuracy_and_logic',
        'question_quality'
    )
    @classmethod
    def validate_binary_metrics(cls, v: MetricResult) -> MetricResult:
        """Ensure reading-specific metrics are binary (0.0 or 1.0)."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Reading metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v

