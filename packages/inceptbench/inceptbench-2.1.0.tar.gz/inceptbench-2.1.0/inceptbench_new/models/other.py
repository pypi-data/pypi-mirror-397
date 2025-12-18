"""
Data models for other educational content evaluation.

This module defines the Pydantic models used for evaluating general educational
content that doesn't fit into specific categories (question, quiz, reading).
"""

from pydantic import Field, field_validator

from .base import BaseEvaluationResult, MetricResult


class OtherEvaluationResult(BaseEvaluationResult):
    """
    Evaluation result for general educational content.
    
    Includes the required metrics (overall, factual_accuracy, educational_accuracy)
    plus general educational content metrics.
    
    All metrics except 'overall' are binary (0.0 or 1.0).
    """
    
    content_type: str = Field(default="other", description="Type of content (other)")
    
    # Other content-specific metrics (all binary)
    educational_value: MetricResult = Field(
        ...,
        description="Whether content provides meaningful learning opportunities"
    )
    
    direct_instruction_alignment: MetricResult = Field(
        ...,
        description="Whether content follows Direct Instruction pedagogical principles"
    )
    
    content_appropriateness: MetricResult = Field(
        ...,
        description="Whether content is suitable for target audience and context"
    )
    
    clarity_and_organization: MetricResult = Field(
        ...,
        description="Whether content is well-structured, clear, and organized"
    )
    
    engagement: MetricResult = Field(
        ...,
        description="Whether content is engaging and motivating for learners"
    )
    
    @field_validator(
        'educational_value',
        'direct_instruction_alignment',
        'content_appropriateness',
        'clarity_and_organization',
        'engagement'
    )
    @classmethod
    def validate_binary_metrics(cls, v: MetricResult) -> MetricResult:
        """Ensure other content metrics are binary (0.0 or 1.0)."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Other content metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v

