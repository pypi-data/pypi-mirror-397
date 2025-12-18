"""
FastAPI REST API for Educational Content Evaluator.

This module provides a REST API for evaluating educational content across
multiple dimensions including accuracy, curriculum alignment, and engagement.

The API is designed to work seamlessly with both AWS Lambda (via Mangum)
and traditional server deployments (EC2, Docker, etc.).

Supports both simple string content and structured content (qs.json format).
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .dependencies import EvaluationServiceDep, APIKeyDep
from .models import (
    CurriculumsResponse,
    ErrorResponse,
    EvaluationRequest,
    EvaluationResponse,
    FailedItem,
    HealthResponse,
    InceptBenchEvaluation,
    ItemEvaluation,
    MetricScore,
)
from ..config.settings import settings

logger = logging.getLogger(__name__)

# API Version
API_VERSION = "2.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting Educational Content Evaluator API v{API_VERSION}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Educational Content Evaluator API")


# Create FastAPI application
app = FastAPI(
    title="Educational Content Evaluator API",
    description=(
        "AI-powered educational content evaluation service that assesses questions, "
        "quizzes, reading passages, and other educational materials across **11+ "
        "quality dimensions** including accuracy, curriculum alignment, clarity, "
        "misconception detection, and more.\n\n"
        "🔐 **Authentication Required**: All evaluation endpoints require an API key. "
        "Click the **Authorize** button (🔓) to enter your API key.\n\n"
        "---\n\n"
        "## Input Formats\n\n"
        "### 1. Simple String Content\n"
        "```json\n"
        '{\n'
        '  "content": "What is 2 + 2?",\n'
        '  "curriculum": "common_core",\n'
        '  "generation_prompt": "Optional prompt used to generate content"\n'
        "}\n"
        "```\n\n"
        "### 2. Structured Content (generated_content)\n\n"
        "#### MCQ (Multiple Choice Question)\n"
        "```json\n"
        '{\n'
        '  "generated_content": [\n'
        '    {\n'
        '      "id": "q1",\n'
        '      "request": {\n'
        '        "grade": "7",\n'
        '        "subject": "mathematics",\n'
        '        "type": "mcq",\n'
        '        "difficulty": "medium",\n'
        '        "locale": "en-US",\n'
        '        "skills": {\n'
        '          "lesson_title": "Solving Linear Equations",\n'
        '          "substandard_id": "CCSS.MATH.7.EE.A.1",\n'
        '          "substandard_description": "Solve equations in one variable"\n'
        '        },\n'
        '        "instruction": "Create a two-step equation"\n'
        '      },\n'
        '      "content": {\n'
        '        "question": "Solve for x: 3x + 7 = 22",\n'
        '        "answer": "C",\n'
        '        "answer_explanation": "Subtract 7, then divide by 3",\n'
        '        "answer_options": [\n'
        '          {"key": "A", "text": "3"},\n'
        '          {"key": "B", "text": "4"},\n'
        '          {"key": "C", "text": "5"},\n'
        '          {"key": "D", "text": "6"}\n'
        '        ],\n'
        '        "image_url": [],\n'
        '        "additional_details": "Optional notes"\n'
        '      }\n'
        '    }\n'
        '  ]\n'
        "}\n"
        "```\n\n"
        "#### Fill-in Question\n"
        "```json\n"
        '{\n'
        '  "generated_content": [\n'
        '    {\n'
        '      "id": "fill1",\n'
        '      "request": {\n'
        '        "grade": "4",\n'
        '        "subject": "english",\n'
        '        "type": "fill-in"\n'
        '      },\n'
        '      "content": {\n'
        '        "question": "The capital of France is ____.",\n'
        '        "answer": "Paris",\n'
        '        "answer_explanation": "Paris is the capital city of France."\n'
        '      }\n'
        '    }\n'
        '  ]\n'
        "}\n"
        "```\n\n"
        "#### Article\n"
        "```json\n"
        '{\n'
        '  "generated_content": [\n'
        '    {\n'
        '      "id": "article1",\n'
        '      "request": {\n'
        '        "grade": "6",\n'
        '        "subject": "science",\n'
        '        "type": "article"\n'
        '      },\n'
        '      "content": {\n'
        '        "content": "# Photosynthesis\\n\\nPhotosynthesis is..."\n'
        '      }\n'
        '    }\n'
        '  ]\n'
        "}\n"
        "```\n\n"
        "**Optional Fields:** `type`, `difficulty`, `locale`, `skills`, `instruction`, `image_url`, `additional_details`\n\n"
        "---\n\n"
        "## Performance\n\n"
        "- **Parallel Processing**: All items are evaluated concurrently for optimal speed\n"
        "- **Single Endpoint**: Use `/evaluate` for both single and batch evaluations (1-100 items)\n"
        "- **Fast**: Multiple items complete in the same time as the slowest individual item"
    ),
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware (configure for your deployment)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Configure OpenAPI schema with security
def custom_openapi():
    """
    Customize OpenAPI schema to include Bearer token authentication.
    
    This adds the security scheme to the OpenAPI spec, which makes
    Swagger UI display the "Authorize" button.
    """
    if app.openapi_schema:
        return app.openapi_schema
       
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "HTTPBearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "API Key",
            "description": (
                "Enter your API key in the format: `your-api-key-here`\n\n"
                "The key will be sent as: `Authorization: Bearer <your-api-key>`"
            )
        }
    }
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


# Exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """Handle ValueError exceptions."""
    logger.warning(f"ValueError: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="ValidationError",
            message=str(exc)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            detail=str(exc) if settings.LOG_LEVEL == "DEBUG" else None
        ).model_dump()
    )


# API Endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"],
    summary="Health check endpoint",
    description="Check if the service is healthy and get version information"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns service health status and version information.
    """
    return HealthResponse(
        status="healthy",
        version=API_VERSION,
        service="Educational Content Evaluator"
    )


@app.get(
    "/curriculums",
    response_model=CurriculumsResponse,
    tags=["Metadata"],
    summary="List available curriculums",
    description=(
        "Get information about curriculum support. The evaluation service uses "
        "InceptAPI for curriculum search, which maintains the authoritative list "
        "of supported curricula. This endpoint returns the default curriculum; "
        "other curricula may be supported - the API will return an error if an "
        "unsupported curriculum is requested."
    )
)
async def list_curriculums() -> CurriculumsResponse:
    """
    List curriculum information.
    
    Returns the default curriculum. The InceptAPI handles curriculum validation
    and will return descriptive errors if an unsupported curriculum is requested.
    """
    return CurriculumsResponse(
        curriculums=[settings.DEFAULT_CURRICULUM],
        default=settings.DEFAULT_CURRICULUM
    )


@app.post(
    "/evaluate",
    response_model=EvaluationResponse,
    tags=["Evaluation"],
    summary="Evaluate educational content",
    description=(
        "Evaluate educational content (questions, quizzes, reading passages, etc.) "
        "across **11+ quality dimensions**. Returns structured evaluation results "
        "with scores, reasoning, and suggested improvements.\n\n"
        "**Accepts:**\n"
        "- `content`: Plain text string with optional `curriculum` and `generation_prompt`\n"
        "- `generated_content`: Array of structured content items (mcq, fill-in, article)\n\n"
        "Only one of these should be provided per request.\n\n"
        "**Evaluation Dimensions:**\n"
        "For **Questions** (MCQ/Fill-in), returns:\n"
        "- overall, factual_accuracy, educational_accuracy\n"
        "- curriculum_alignment, clarity_precision\n"
        "- reveals_misconceptions, difficulty_alignment\n"
        "- passage_reference, distractor_quality\n"
        "- stimulus_quality, mastery_learning_alignment\n"
        "- localization_quality, weighted_score\n\n"
        "For **Articles/Content**, returns:\n"
        "- overall, factual_accuracy, educational_accuracy\n"
        "- teaching_quality, worked_examples, reading_level_match\n\n"
        "**Performance:**\n"
        "All items are processed in parallel for optimal performance, whether you send "
        "1 item or 100 items. This ensures fast evaluation times for both single and "
        "batch requests.\n\n"
        "**Error Handling:**\n"
        "- If an item fails, evaluation continues for remaining items (partial success)\n"
        "- Successful evaluations are returned; failed items are logged and omitted\n"
        "- Check the returned `evaluations` dict to see which items succeeded\n\n"
        "**Limits:**\n"
        "- Maximum 100 items per request"
    ),
    response_description="Structured evaluation results with 11+ content-specific quality metrics"
)
async def evaluate_content(
    request: EvaluationRequest,
    service: EvaluationServiceDep,
    api_key: APIKeyDep
) -> EvaluationResponse:
    """
    Evaluate educational content.
    
    This endpoint accepts educational content and:
    1. Extracts content from simple string or structured format
    2. Classifies the content type (question, quiz, reading passage, etc.)
    3. Routes to the appropriate evaluator
    4. Processes all items in parallel for optimal performance
    5. Returns structured evaluation results with scores and suggestions
    
    Args:
        request: EvaluationRequest with content or generated_content array
        service: Injected EvaluationService instance
        api_key: API key for authentication
    
    Returns:
        EvaluationResponse with:
        - request_id: Unique identifier for the request
        - evaluations: Dict of evaluations keyed by item ID
        - evaluation_time_seconds: Total evaluation time
        - inceptbench_version: Version of InceptBench
    
    Raises:
        HTTPException: If evaluation fails or validation errors occur
    """

    start_time = time.time()
    request_id = str(uuid4())
    
    # Get items for evaluation
    items = request.get_items_for_evaluation()
    
    logger.info(
        f"[{request_id}] Evaluating {len(items)} item(s) in parallel"
    )
    
    async def evaluate_single(item_id: str, content_str: str, generation_prompt: Optional[str]) -> tuple[str, ItemEvaluation, Optional[str]]:
        """Evaluate a single item, catching errors."""
        try:
            # Use curriculum from request if simple content, otherwise use default
            curriculum = request.curriculum if request.content else "common_core"
            
            # Perform evaluation
            result = await service.evaluate(
                content=content_str,
                curriculum=curriculum,
                generation_prompt=generation_prompt
            )
            
            result_dict = result.model_dump()
            
            # Build InceptBenchEvaluation with all possible dimensions
            inceptbench_eval = InceptBenchEvaluation(
                content_type=result_dict.get("content_type", "unknown"),
                overall=MetricScore(**result_dict["overall"]) if "overall" in result_dict else None,
                factual_accuracy=MetricScore(**result_dict["factual_accuracy"]) if "factual_accuracy" in result_dict else None,
                educational_accuracy=MetricScore(**result_dict["educational_accuracy"]) if "educational_accuracy" in result_dict else None,
                # Question-specific metrics (all 11 dimensions)
                curriculum_alignment=MetricScore(**result_dict["curriculum_alignment"]) if "curriculum_alignment" in result_dict else None,
                clarity_precision=MetricScore(**result_dict["clarity_precision"]) if "clarity_precision" in result_dict else None,
                reveals_misconceptions=MetricScore(**result_dict["reveals_misconceptions"]) if "reveals_misconceptions" in result_dict else None,
                difficulty_alignment=MetricScore(**result_dict["difficulty_alignment"]) if "difficulty_alignment" in result_dict else None,
                passage_reference=MetricScore(**result_dict["passage_reference"]) if "passage_reference" in result_dict else None,
                distractor_quality=MetricScore(**result_dict["distractor_quality"]) if "distractor_quality" in result_dict else None,
                stimulus_quality=MetricScore(**result_dict["stimulus_quality"]) if "stimulus_quality" in result_dict else None,
                mastery_learning_alignment=MetricScore(**result_dict["mastery_learning_alignment"]) if "mastery_learning_alignment" in result_dict else None,
                localization_quality=MetricScore(**result_dict["localization_quality"]) if "localization_quality" in result_dict else None,
                # Article/content-specific metrics
                teaching_quality=MetricScore(**result_dict["teaching_quality"]) if "teaching_quality" in result_dict else None,
                worked_examples=MetricScore(**result_dict["worked_examples"]) if "worked_examples" in result_dict else None,
                reading_level_match=MetricScore(**result_dict["reading_level_match"]) if "reading_level_match" in result_dict else None,
                weighted_score=result_dict.get("weighted_score", result_dict.get("overall", {}).get("score", 0.0))
            )
            
            # Build ItemEvaluation
            item_eval = ItemEvaluation(
                inceptbench_new_evaluation=inceptbench_eval,
                score=result_dict.get("overall", {}).get("score", 0.0)
            )
            
            logger.info(
                f"[{request_id}] Item {item_id} evaluated successfully. "
                f"Type: {inceptbench_eval.content_type}, Score: {item_eval.score:.2f}"
            )
            
            return (item_id, item_eval, None)
            
        except Exception as e:
            logger.error(f"[{request_id}] Item {item_id} failed: {e}")
            return (item_id, None, str(e))
    
    try:
        # Prepare tasks for all items
        tasks = []
        for item_id, content_str, generation_prompt in items:
            tasks.append(evaluate_single(item_id, content_str, generation_prompt))
        
        # Process all items in parallel
        results = await asyncio.gather(*tasks)
        
        # Build evaluations dict and collect failures
        evaluations = {}
        failed_items = []
        for item_id, item_eval, error in results:
            if error:
                logger.warning(f"[{request_id}] Item {item_id} failed: {error}")
                failed_items.append((item_id, error))
            else:
                evaluations[item_id] = item_eval
        
        # Calculate total time
        evaluation_time = time.time() - start_time
        
        # Log summary
        if failed_items:
            logger.warning(
                f"[{request_id}] Evaluation complete with partial success. "
                f"Total: {len(results)}, Successful: {len(evaluations)}, "
                f"Failed: {len(failed_items)}, Time: {evaluation_time:.2f}s"
            )
        else:
            logger.info(
                f"[{request_id}] Evaluation complete. "
                f"Items: {len(evaluations)}, Time: {evaluation_time:.2f}s"
            )
        
        # Build failed items list if any failures occurred
        failed_items_list = None
        if failed_items:
            failed_items_list = [
                FailedItem(item_id=item_id, error=error)
                for item_id, error in failed_items
            ]
        
        # Return response with successful evaluations and failure information
        return EvaluationResponse(
            request_id=request_id,
            evaluations=evaluations,
            evaluation_time_seconds=evaluation_time,
            inceptbench_version=API_VERSION,
            failed_items=failed_items_list
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ValueError as e:
        # Validation errors
        logger.warning(f"[{request_id}] Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Unexpected errors
        logger.error(f"[{request_id}] Error during evaluation: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evaluation failed: {str(e)}"
        )


# Root endpoint
@app.get(
    "/",
    include_in_schema=False,
    tags=["Root"]
)
async def root():
    """Root endpoint - provides API information."""
    return {
        "service": "Educational Content Evaluator API",
        "version": API_VERSION,
        "inceptbench_version": API_VERSION,
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "evaluate": "POST /evaluate - Evaluate single or multiple items (parallel processing)",
            "curriculums": "GET /curriculums",
            "health": "GET /health"
        },
        "supported_formats": [
            "Simple string content (content field with curriculum and generation_prompt)",
            "Structured content array (generated_content field with mcq, fill-in, or article items)"
        ],
        "content_types": [
            "mcq - Multiple choice questions",
            "fill-in - Fill in the blank questions",
            "article - Reading passages and articles"
        ],
        "performance": {
            "processing": "All items processed in parallel",
            "supports": "1-100 items per request",
            "note": "Multiple items complete in the time of the slowest item"
        }
    }


# For local development and testing
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "inceptbench_new.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
