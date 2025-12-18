"""
API request and response models.

This module defines Pydantic models for API input validation and response formatting.
Supports both simple string content and structured educational content with new schema.
"""

from typing import Any, Optional, Union, Literal
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


# New Schema Models

class Skills(BaseModel):
    """Skills information for content."""
    
    lesson_title: Optional[str] = Field(default=None, description="Title of the lesson")
    substandard_id: Optional[str] = Field(default=None, description="Substandard identifier")
    substandard_description: Optional[str] = Field(default=None, description="Description of the substandard")


class RequestMetadata(BaseModel):
    """Request metadata for content generation."""
    
    grade: str = Field(..., description="Grade level")
    subject: str = Field(..., description="Subject area")
    type: Optional[Literal["mcq", "fill-in", "article"]] = Field(default=None, description="Content type")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level")
    locale: Optional[str] = Field(default=None, description="Locale/language code")
    skills: Optional[Skills] = Field(default=None, description="Skills information")
    instruction: Optional[str] = Field(default=None, description="Content instruction/prompt")


class AnswerOption(BaseModel):
    """Answer option for MCQ questions."""
    
    key: str = Field(..., description="Option key (A, B, C, D, E)")
    text: str = Field(..., description="Option text")


class ContentMCQ(BaseModel):
    """Content structure for MCQ type."""
    
    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="Correct answer key (A, B, C, D, or E)")
    answer_explanation: str = Field(..., description="Explanation for the answer")
    answer_options: list[AnswerOption] = Field(..., description="List of answer options")
    image_url: Optional[list[str]] = Field(default=None, description="List of image URLs")
    additional_details: Optional[str] = Field(default=None, description="Optional additional details")
    
    @model_validator(mode='after')
    def validate_mcq(self) -> 'ContentMCQ':
        """Validate MCQ has answer_options."""
        if not self.answer_options or len(self.answer_options) == 0:
            raise ValueError("MCQ must have at least one answer option")
        
        # Validate answer key exists in options
        valid_keys = {opt.key for opt in self.answer_options}
        if self.answer not in valid_keys:
            raise ValueError(f"Answer '{self.answer}' must be one of the option keys: {valid_keys}")
        
        return self


class ContentFillIn(BaseModel):
    """Content structure for fill-in type."""
    
    question: str = Field(..., description="The question text")
    answer: str = Field(..., description="Correct answer")
    answer_explanation: str = Field(..., description="Explanation for the answer")
    image_url: Optional[list[str]] = Field(default=None, description="List of image URLs")
    additional_details: Optional[str] = Field(default=None, description="Optional additional details")
    
    @model_validator(mode='after')
    def validate_fill_in(self) -> 'ContentFillIn':
        """Validate fill-in doesn't have answer_options."""
        # Fill-in should not have answer_options (that's for MCQ)
        return self


class ContentArticle(BaseModel):
    """Content structure for article type."""
    
    content: str = Field(..., description="Article content in markdown format")
    additional_details: Optional[str] = Field(default=None, description="Optional additional details")
    
    @model_validator(mode='after')
    def validate_article(self) -> 'ContentArticle':
        """Validate article has content."""
        if not self.content or not self.content.strip():
            raise ValueError("Article content cannot be empty")
        return self


class GeneratedContentItem(BaseModel):
    """Single item in generated_content array."""
    
    id: str = Field(..., description="Content identifier")
    request: RequestMetadata = Field(..., description="Request metadata")
    content: Union[ContentMCQ, ContentFillIn, ContentArticle] = Field(..., description="Content structure (varies by type)")
    
    @model_validator(mode='after')
    def validate_content_type(self) -> 'GeneratedContentItem':
        """Validate content structure matches the request type (if type is provided)."""
        content_type = self.request.type
        
        # If type is provided, validate it matches the content structure
        if content_type is not None:
            if content_type == "mcq" and not isinstance(self.content, ContentMCQ):
                raise ValueError("Content must be ContentMCQ when type is 'mcq'")
            elif content_type == "fill-in" and not isinstance(self.content, ContentFillIn):
                raise ValueError("Content must be ContentFillIn when type is 'fill-in'")
            elif content_type == "article" and not isinstance(self.content, ContentArticle):
                raise ValueError("Content must be ContentArticle when type is 'article'")
        else:
            # If type is not provided, infer it from content structure and set it
            if isinstance(self.content, ContentMCQ):
                self.request.type = "mcq"
            elif isinstance(self.content, ContentFillIn):
                self.request.type = "fill-in"
            elif isinstance(self.content, ContentArticle):
                self.request.type = "article"
        
        return self
    
    def to_evaluation_string(self) -> str:
        """Convert item to string for evaluation."""
        parts = []
        
        # For MCQ
        if isinstance(self.content, ContentMCQ):
            parts.append(self.content.question)
            parts.append("\nAnswer Options:")
            for option in self.content.answer_options:
                parts.append(f"  {option.key}) {option.text}")
            parts.append(f"\nCorrect Answer: {self.content.answer}")
            parts.append(f"\nExplanation: {self.content.answer_explanation}")
            
            if self.content.image_url:
                parts.append(f"\nImages: {', '.join(self.content.image_url)}")
            
            if self.content.additional_details:
                parts.append(f"\nAdditional Details: {self.content.additional_details}")
        
        # For Fill-in
        elif isinstance(self.content, ContentFillIn):
            parts.append(self.content.question)
            parts.append(f"\nCorrect Answer: {self.content.answer}")
            parts.append(f"\nExplanation: {self.content.answer_explanation}")
            
            if self.content.image_url:
                parts.append(f"\nImages: {', '.join(self.content.image_url)}")
            
            if self.content.additional_details:
                parts.append(f"\nAdditional Details: {self.content.additional_details}")
        
        # For Article
        elif isinstance(self.content, ContentArticle):
            parts.append(self.content.content)
            
            if self.content.additional_details:
                parts.append(f"\nAdditional Details: {self.content.additional_details}")
        
        return "\n".join(parts)


class EvaluationRequest(BaseModel):
    """
    Request model for content evaluation endpoint.
    
    Accepts either:
    - Simple string content in 'content' field with optional 'curriculum' and 'generation_prompt'
    - Structured content array in 'generated_content' field
    
    Only one of these should be provided.
    """
    
    # Simple string content
    content: Optional[str] = Field(
        None,
        description="The educational content to evaluate as a plain string",
        max_length=100000
    )
    
    # Structured content array (new format)
    generated_content: Optional[list[GeneratedContentItem]] = Field(
        None,
        description="Array of structured content items to evaluate",
        min_length=1,
        max_length=100
    )
    
    # Fields for simple content only
    curriculum: Optional[str] = Field(
        default="common_core",
        description="The curriculum to use for evaluation (only for simple content)",
        pattern="^[a-z_]+$"
    )
    generation_prompt: Optional[str] = Field(
        None,
        description="Optional prompt used to generate the content (only for simple content)",
        max_length=50000
    )
    
    @model_validator(mode='after')
    def validate_content_provided(self) -> 'EvaluationRequest':
        """Ensure exactly one content type is provided."""
        has_content = self.content is not None
        has_generated_content = self.generated_content is not None
        
        if not has_content and not has_generated_content:
            raise ValueError(
                "Either 'content' or 'generated_content' must be provided"
            )
        if has_content and has_generated_content:
            raise ValueError(
                "Only one of 'content' or 'generated_content' should be provided"
            )
        
        # Validate content is not empty if provided as string
        if self.content is not None and not self.content.strip():
            raise ValueError("Content cannot be empty or just whitespace")
        
        # Validate generated_content if provided
        if self.generated_content is not None and len(self.generated_content) == 0:
            raise ValueError("generated_content cannot be empty array")
        
        return self
    
    def is_batch(self) -> bool:
        """Check if this is a batch request (multiple items in generated_content)."""
        return self.generated_content is not None and len(self.generated_content) > 1
    
    def get_items_for_evaluation(self) -> list[tuple[str, str, Optional[str]]]:
        """
        Get list of (id, content_string, generation_prompt) tuples for evaluation.
        
        Returns:
            List of tuples: (item_id, content_as_string, generation_prompt)
        """
        items = []
        
        if self.content:
            # Simple content
            items.append(("content_1", self.content, self.generation_prompt))
        elif self.generated_content:
            # Structured content
            for item in self.generated_content:
                content_str = item.to_evaluation_string()
                # Use instruction as generation_prompt
                prompt = item.request.instruction if item.request.instruction else None
                items.append((item.id, content_str, prompt))
        
        return items
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "content": "What is the capital of France?",
                    "curriculum": "common_core",
                    "generation_prompt": "Generate a geography question"
                },
                {
                    "generated_content": [
                        {
                            "id": "q1",
                            "request": {
                                "grade": "7",
                                "subject": "mathematics",
                                "type": "mcq",
                                "difficulty": "medium",
                                "locale": "en-US",
                                "skills": {
                                    "lesson_title": "Solving Linear Equations",
                                    "substandard_id": "CCSS.MATH.7.EE.A.1",
                                    "substandard_description": "Solve linear equations in one variable"
                                },
                                "instruction": "Create a linear equation problem"
                            },
                            "content": {
                                "question": "What is the value of x in 3x + 7 = 22?",
                                "answer": "C",
                                "answer_explanation": "Subtract 7 from both sides: 3x = 15, then divide by 3: x = 5",
                                "answer_options": [
                                    {"key": "A", "text": "3"},
                                    {"key": "B", "text": "4"},
                                    {"key": "C", "text": "5"},
                                    {"key": "D", "text": "6"}
                                ]
                            }
                        }
                    ]
                },
                {
                    "generated_content": [
                        {
                            "id": "q2",
                            "request": {
                                "grade": "5",
                                "subject": "mathematics"
                            },
                            "content": {
                                "question": "What is 2 + 2?",
                                "answer": "B",
                                "answer_explanation": "2 + 2 = 4",
                                "answer_options": [
                                    {"key": "A", "text": "3"},
                                    {"key": "B", "text": "4"}
                                ]
                            }
                        }
                    ]
                }
            ]
        }
    }


# Response Models

class MetricScore(BaseModel):
    """Individual metric score with reasoning and improvement suggestions."""
    
    score: float = Field(..., ge=0.0, le=1.0, description="Metric score (0.0 to 1.0)")
    reasoning: str = Field(..., description="Detailed reasoning explaining the score")
    suggested_improvements: Optional[str] = Field(None, description="Actionable suggestions for improvement (null if score is perfect)")


class InceptBenchEvaluation(BaseModel):
    """InceptBench evaluation result for a single item with 11+ quality dimensions."""
    
    content_type: str = Field(..., description="Detected content type (question, article, nonfiction_reading, etc.)")
    
    # Core metrics (always present)
    overall: MetricScore = Field(..., description="Overall quality score across all dimensions")
    factual_accuracy: MetricScore = Field(..., description="Factual correctness and mathematical/scientific accuracy")
    educational_accuracy: Optional[MetricScore] = Field(None, description="Appropriateness for target grade level and learning objectives")
    
    # Question-specific metrics (present for MCQ/fill-in questions)
    curriculum_alignment: Optional[MetricScore] = Field(None, description="Alignment with curriculum standards (e.g., Common Core, NGSS)")
    clarity_precision: Optional[MetricScore] = Field(None, description="Whether question is clear, unambiguous, and precisely worded")
    reveals_misconceptions: Optional[MetricScore] = Field(None, description="Whether question effectively reveals and addresses student misconceptions")
    difficulty_alignment: Optional[MetricScore] = Field(None, description="Whether difficulty matches intended grade/skill level")
    passage_reference: Optional[MetricScore] = Field(None, description="Whether question properly references passage/context when applicable")
    distractor_quality: Optional[MetricScore] = Field(None, description="Quality of incorrect answer choices (distractors) if present")
    stimulus_quality: Optional[MetricScore] = Field(None, description="Quality and appropriateness of images, diagrams, or other stimuli")
    mastery_learning_alignment: Optional[MetricScore] = Field(None, description="Whether question supports mastery learning principles and deep understanding")
    localization_quality: Optional[MetricScore] = Field(None, description="Quality of localization and cultural appropriateness")
    
    # Article/content-specific metrics (present for articles and reading passages)
    teaching_quality: Optional[MetricScore] = Field(None, description="Effectiveness of teaching approach and pedagogical structure")
    worked_examples: Optional[MetricScore] = Field(None, description="Quality and presence of worked examples in instructional content")
    reading_level_match: Optional[MetricScore] = Field(None, description="Whether reading level matches target grade (for reading passages)")
    
    weighted_score: float = Field(..., ge=0.0, le=1.0, description="Tier-weighted overall score")


class ItemEvaluation(BaseModel):
    """Evaluation result for a single content item."""
    
    inceptbench_new_evaluation: InceptBenchEvaluation = Field(..., description="InceptBench evaluation details")
    score: float = Field(..., description="Overall score for the item")


class FailedItem(BaseModel):
    """Information about a failed evaluation item."""
    
    item_id: str = Field(..., description="ID of the failed item")
    error: str = Field(..., description="Error message")


class EvaluationResponse(BaseModel):
    """Response model for evaluation endpoints."""
    
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique request identifier")
    evaluations: dict[str, ItemEvaluation] = Field(..., description="Evaluations keyed by item ID (only successful items)")
    evaluation_time_seconds: float = Field(..., description="Total evaluation time in seconds")
    inceptbench_version: str = Field(..., description="InceptBench version")
    failed_items: Optional[list[FailedItem]] = Field(default=None, description="List of items that failed evaluation (null if all succeeded)")
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "request_id": "550e8400-e29b-41d4-a716-446655440000",
                    "evaluations": {
                        "q1": {
                            "inceptbench_new_evaluation": {
                                "content_type": "question",
                                "overall": {
                                    "score": 0.9,
                                    "reasoning": "Strong question with clear wording and correct answer. Minor improvement needed in distractor quality.",
                                    "suggested_improvements": "Consider using distractors that reflect common misconceptions."
                                },
                                "factual_accuracy": {
                                    "score": 1.0,
                                    "reasoning": "The correct answer is mathematically accurate.",
                                    "suggested_improvements": None
                                },
                                "educational_accuracy": {
                                    "score": 1.0,
                                    "reasoning": "Appropriate for the target grade level.",
                                    "suggested_improvements": None
                                },
                                "curriculum_alignment": {
                                    "score": 1.0,
                                    "reasoning": "Aligns with Common Core standards for linear equations.",
                                    "suggested_improvements": None
                                },
                                "clarity_precision": {
                                    "score": 1.0,
                                    "reasoning": "Question is clear and unambiguous.",
                                    "suggested_improvements": None
                                },
                                "reveals_misconceptions": {
                                    "score": 0.0,
                                    "reasoning": "Distractors are generic and don't target specific misconceptions.",
                                    "suggested_improvements": "Use distractors like 15 (forgot to divide) or 29/3 (added instead of subtracted)."
                                },
                                "difficulty_alignment": {
                                    "score": 1.0,
                                    "reasoning": "Appropriate difficulty for grade 7 students.",
                                    "suggested_improvements": None
                                },
                                "passage_reference": {
                                    "score": 1.0,
                                    "reasoning": "No passage required; question is self-contained.",
                                    "suggested_improvements": None
                                },
                                "distractor_quality": {
                                    "score": 1.0,
                                    "reasoning": "Options are grammatically parallel and plausible.",
                                    "suggested_improvements": None
                                },
                                "stimulus_quality": {
                                    "score": 1.0,
                                    "reasoning": "No stimulus needed for this algebraic question.",
                                    "suggested_improvements": None
                                },
                                "mastery_learning_alignment": {
                                    "score": 0.0,
                                    "reasoning": "Tests procedural skill without deeper conceptual understanding.",
                                    "suggested_improvements": "Add a follow-up asking why a particular step is valid."
                                },
                                "localization_quality": {
                                    "score": 1.0,
                                    "reasoning": "Neutral mathematical content with no cultural dependencies.",
                                    "suggested_improvements": None
                                },
                                "weighted_score": 0.8387
                            },
                            "score": 0.9
                        }
                    },
                    "evaluation_time_seconds": 12.34,
                    "inceptbench_version": "x.y.z",
                    "failed_items": None
                },
                {
                    "request_id": "550e8400-e29b-41d4-a716-446655440001",
                    "evaluations": {
                        "q1": {
                            "inceptbench_new_evaluation": {
                                "content_type": "question",
                                "overall": {"score": 0.9, "reasoning": "Good question", "suggested_improvements": None},
                                "factual_accuracy": {"score": 1.0, "reasoning": "Accurate", "suggested_improvements": None},
                                "educational_accuracy": {"score": 1.0, "reasoning": "Appropriate", "suggested_improvements": None},
                                "weighted_score": 0.9
                            },
                            "score": 0.9
                        }
                    },
                    "evaluation_time_seconds": 8.5,
                    "inceptbench_version": "x.y.z",
                    "failed_items": [
                        {"item_id": "q2", "error": "Invalid content format"},
                        {"item_id": "q3", "error": "Curriculum validation failed"}
                    ]
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="API version")
    service: str = Field(..., description="Service name")


class CurriculumsResponse(BaseModel):
    """Response model for curriculum listing endpoint."""
    
    curriculums: list[str] = Field(..., description="Available curriculum names")
    default: str = Field(..., description="Default curriculum")


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
