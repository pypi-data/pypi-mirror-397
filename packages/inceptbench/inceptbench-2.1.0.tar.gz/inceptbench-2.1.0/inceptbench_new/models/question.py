"""
Data models for question evaluation.

This module defines the Pydantic models used for evaluating individual questions,
including all metrics specific to question content.
"""

from pydantic import Field, field_validator

from .base import BaseEvaluationResult, MetricResult


class QuestionEvaluationResult(BaseEvaluationResult):
    """
    Evaluation result for a single question.
    
    Includes the required metrics (overall, factual_accuracy, educational_accuracy)
    plus question-specific metrics that assess various quality dimensions.
    
    All metrics except 'overall' are binary (0.0 or 1.0).
    """
    
    content_type: str = Field(default="question", description="Type of content (question)")
    
    # Question-specific metrics (all binary)
    curriculum_alignment: MetricResult = Field(
        ...,
        description="Whether question aligns with curriculum standards and learning objectives"
    )
    
    clarity_precision: MetricResult = Field(
        ...,
        description="Whether question is clear, unambiguous, and precisely worded"
    )
    
    reveals_misconceptions: MetricResult = Field(
        ...,
        description="Whether question effectively reveals and addresses student misconceptions"
    )
    
    difficulty_alignment: MetricResult = Field(
        ...,
        description="Whether question difficulty matches intended level and cognitive demand"
    )
    
    passage_reference: MetricResult = Field(
        ...,
        description="Whether question properly references passage/context when applicable"
    )
    
    distractor_quality: MetricResult = Field(
        ...,
        description="Quality of incorrect answer choices (distractors) if present"
    )
    
    stimulus_quality: MetricResult = Field(
        ...,
        description="Quality and appropriateness of images, diagrams, or other stimuli"
    )
    
    mastery_learning_alignment: MetricResult = Field(
        ...,
        description="Whether question supports mastery learning principles and deep understanding"
    )
    
    @field_validator(
        'curriculum_alignment',
        'clarity_precision', 
        'reveals_misconceptions',
        'difficulty_alignment',
        'passage_reference',
        'distractor_quality',
        'stimulus_quality',
        'mastery_learning_alignment'
    )
    @classmethod
    def validate_binary_metrics(cls, v: MetricResult) -> MetricResult:
        """Ensure question-specific metrics are binary (0.0 or 1.0)."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Question metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v

