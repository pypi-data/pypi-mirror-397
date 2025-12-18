"""
Base models for educational content evaluation.

This module defines the core Pydantic models used across all evaluators,
including metric results, evaluation results, and content types.
"""

from abc import ABC
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_serializer

from inceptbench_new.config.tier_scoring import calculate_weighted_score


class ContentType(str, Enum):
    """Types of educational content that can be evaluated."""
    QUESTION = "question"
    QUIZ = "quiz"
    FICTION_READING = "fiction_reading"
    NONFICTION_READING = "nonfiction_reading"
    ARTICLE = "article"
    OTHER = "other"


class MetricResult(BaseModel):
    """
    Result for a single evaluation metric.
    
    Attributes:
        score: Float in [0.0, 1.0]. Binary metrics are 0.0 or 1.0.
               Only 'overall' can have intermediate values.
        reasoning: Explanation for the score given.
        suggested_improvements: Suggestions for improvement. Required if score < 1.0.
    """
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0.0 and 1.0")
    reasoning: str = Field(..., min_length=1, description="Explanation for the score")
    suggested_improvements: Optional[str] = Field(
        None, 
        description="Suggestions for improvement (required if score < 1.0)"
    )
    
    @field_validator('suggested_improvements')
    @classmethod
    def validate_improvements(cls, v: Optional[str], info) -> Optional[str]:
        """Ensure suggested_improvements is provided when score < 1.0."""
        score = info.data.get('score')
        if score is not None and score < 1.0 and not v:
            raise ValueError(
                "suggested_improvements is required when score < 1.0"
            )
        return v
    
    def to_dict(self) -> dict:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class BaseEvaluationResult(BaseModel, ABC):
    """
    Abstract base class for all evaluation results.
    
    All evaluation results must include:
    - content_type: Type of content evaluated
    - overall: Overall assessment (continuous metric)
    - factual_accuracy: Factual correctness (binary)
    - educational_accuracy: Educational intent fulfillment (binary)
    - localization_quality: Cultural/linguistic appropriateness (binary)

    Subclasses add content-type-specific metrics.
    """
    
    model_config = ConfigDict(
        # Serialize using actual runtime type, not annotated type
        # This ensures subcontent_evaluations include all subclass fields
        use_enum_values=True,
    )
    
    content_type: str = Field(..., description="Type of content evaluated")
    overall: MetricResult = Field(..., description="Overall assessment (continuous)")
    factual_accuracy: MetricResult = Field(
        ..., 
        description="Factual correctness (binary)"
    )
    educational_accuracy: MetricResult = Field(
        ..., 
        description="Educational intent fulfillment (binary)"
    )
    localization_quality: MetricResult = Field(
        ...,
        description="Cultural and linguistic appropriateness for target audience (binary)"
    )

    # Hierarchical content support
    subcontent_evaluations: Optional[List['BaseEvaluationResult']] = Field(
        None,
        description="Evaluation results for nested content (e.g., questions within a quiz)"
    )

    @field_validator('factual_accuracy', 'educational_accuracy', 'localization_quality')
    @classmethod
    def validate_binary_metric(cls, v: MetricResult) -> MetricResult:
        """Ensure binary metrics have scores of exactly 0.0 or 1.0."""
        if v.score not in (0.0, 1.0):
            raise ValueError(
                f"Binary metrics must have score of 0.0 or 1.0, got {v.score}"
            )
        return v
    
    @model_serializer(mode='wrap')
    def _serialize_model(self, serializer: Any) -> dict:
        """
        Custom serializer to ensure subcontent_evaluations include all fields
        and appear last in the output (after all parent metrics).
        
        This wraps the default serializer and:
        1. Explicitly serializes each subcontent evaluation using its actual runtime type
        2. Moves subcontent_evaluations to the end of the dictionary (even if None)
        """
        # Get default serialization
        data = serializer(self)
        
        # Always move subcontent_evaluations to the end if present
        if 'subcontent_evaluations' in data:
            # Remove from current position
            subcontent = data.pop('subcontent_evaluations')
            
            # If we have actual subcontent, serialize each item with all its fields
            if subcontent:
                subcontent_serialized = [
                    # Explicitly call model_dump on each item to get all its fields
                    item.model_dump(mode='python') if hasattr(item, 'model_dump')
                    else item
                    for item in self.subcontent_evaluations
                ]
                # Add back at the end with full serialization
                data['subcontent_evaluations'] = subcontent_serialized
            else:
                # Add back as None at the end
                data['subcontent_evaluations'] = subcontent
        
        return data
    
    def _get_metric_scores(self) -> Dict[str, float]:
        """Extract all metric scores from this result."""
        scores = {}
        for field_name in type(self).model_fields:
            if field_name in ('content_type', 'subcontent_evaluations', 'overall'):
                continue
            value = getattr(self, field_name, None)
            if isinstance(value, MetricResult):
                scores[field_name] = value.score
        return scores

    @computed_field
    @property
    def weighted_score(self) -> float:
        """
        Tier-weighted score based on metric importance.

        Critical metrics (factual_accuracy, educational_accuracy) are weighted 2x.
        Important metrics (curriculum_alignment, clarity, etc.) are weighted 1.5x.
        Enhancement metrics (localization, engagement, etc.) are weighted 1x.
        """
        scores = self._get_metric_scores()
        result = calculate_weighted_score(scores)
        return round(result, 4) if result is not None else 0.0

    def to_json(self) -> str:
        """Convert to JSON string."""
        return self.model_dump_json(indent=2)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return self.model_dump()


class EvaluationRequest(BaseModel):
    """
    Request model for content evaluation.
    
    Attributes:
        content: The educational content to evaluate (any string, may contain image URLs)
        curriculum: Curriculum to use for evaluation (defaults to "common_core")
        generation_prompt: Optional prompt used to generate the content (for AI-generated content)
    """
    content: str = Field(..., min_length=1, description="Content to evaluate")
    curriculum: str = Field(
        "common_core", 
        description="Curriculum for evaluation"
    )
    generation_prompt: Optional[str] = Field(
        None,
        description="Optional prompt used to generate the content (useful for evaluating AI-generated content)"
    )
    
    @field_validator('content')
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        """Ensure content is not just whitespace."""
        if not v.strip():
            raise ValueError("Content cannot be empty or just whitespace")
        return v

