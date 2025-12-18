"""
Educational Content Evaluator REST API.

This package provides a production-ready FastAPI application for evaluating
educational content. The API is designed to work seamlessly with both:
- AWS Lambda (serverless) via Mangum adapter
- Traditional servers (EC2, Docker) via Uvicorn/Gunicorn

Key Features:
- Content type classification (questions, quizzes, reading passages, etc.)
- Comprehensive quality evaluation across multiple dimensions
- Curriculum-aligned assessment (Common Core, etc.)
- Image analysis and object counting
- Structured JSON responses with reasoning and suggestions

Quick Start (Local Development):
    uvicorn src.api.main:app --reload

Quick Start (Docker):
    docker-compose up

Quick Start (Lambda):
    sam build && sam deploy --guided

See README.md for detailed deployment instructions.
"""

from .main import app

__all__ = ["app"]

