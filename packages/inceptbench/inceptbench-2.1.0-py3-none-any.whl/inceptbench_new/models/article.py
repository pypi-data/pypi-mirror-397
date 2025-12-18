"""
Article evaluation result model.

This module defines the Pydantic model for article evaluation results,
including article-specific metrics for instructional content quality.
"""

from pydantic import Field, field_validator

from .base import BaseEvaluationResult, MetricResult


class ArticleEvaluationResult(BaseEvaluationResult):
    """
    Evaluation result for an educational article.
    
    Articles are instructional content designed to teach concepts or skills,
    typically including explanatory content, worked examples, and practice problems.
    
    Includes the required metrics (overall, factual_accuracy, educational_accuracy)
    plus article-specific metrics that assess instructional quality.
    
    All metrics except 'overall' are binary (0.0 or 1.0).
    """
    
    content_type: str = Field(default="article", description="Type of content (article)")
    
    # Article-specific metrics (all binary)
    curriculum_alignment: MetricResult = Field(
        ...,
        description="Whether article aligns with curriculum standards and learning objectives"
    )
    
    teaching_quality: MetricResult = Field(
        ...,
        description="Quality of instructional approach and pedagogical effectiveness"
    )
    
    worked_examples: MetricResult = Field(
        ...,
        description="Quality and appropriateness of worked examples provided"
    )
    
    practice_problems: MetricResult = Field(
        ...,
        description="Quality and appropriateness of practice problems included"
    )
    
    follows_direct_instruction: MetricResult = Field(
        ...,
        description="Whether article follows direct instruction principles effectively"
    )
    
    stimulus_quality: MetricResult = Field(
        ...,
        description="Quality and appropriateness of images, diagrams, or other stimuli"
    )
    
    diction_and_sentence_structure: MetricResult = Field(
        ...,
        description="Appropriateness of language, vocabulary, and sentence complexity for grade level"
    )
    
    @field_validator(
        'curriculum_alignment',
        'teaching_quality',
        'worked_examples',
        'practice_problems',
        'follows_direct_instruction',
        'stimulus_quality',
        'diction_and_sentence_structure'
    )
    @classmethod
    def validate_binary_metrics(cls, v: MetricResult) -> MetricResult:
        """Ensure article-specific metrics are binary (0.0 or 1.0)."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Article metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v

