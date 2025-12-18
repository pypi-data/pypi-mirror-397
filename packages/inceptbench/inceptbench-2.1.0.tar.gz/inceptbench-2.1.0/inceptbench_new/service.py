"""
Main evaluation service for educational content.

This module provides the primary service that orchestrates the complete
evaluation flow: classification → routing → evaluation.
"""

import logging
import time
from typing import Optional

from .classifier.content_classifier import ContentClassifier
from .decomposer.content_decomposer import ContentDecomposer
from .orchestrator.evaluation_orchestrator import EvaluationOrchestrator
from .models.base import BaseEvaluationResult
from .config.settings import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """
    Main service for evaluating educational content.
    
    Provides comprehensive hierarchical evaluation:
    1. Classifies content type using LLM
    2. Decomposes into nested structure (e.g., quiz → questions, reading passage → quiz → questions)
    3. Evaluates bottom-up with context propagation:
       - Children evaluated first (in parallel where possible)
       - Parents evaluated with knowledge of child results
       - All nodes receive root content as context
    4. Returns nested evaluation results with child evaluations
    
    This is the primary interface that external systems (CLI, API) should use.
    """
    
    def __init__(self):
        """Initialize the evaluation service with classifier, decomposer, and orchestrator."""
        # Validate API keys on initialization
        settings.validate_api_keys()
        
        self.classifier = ContentClassifier()
        self.decomposer = ContentDecomposer()
        self.orchestrator = EvaluationOrchestrator(client=None)  # Orchestrator creates its own evaluators
        logger.info("Evaluation service initialized")
    
    async def evaluate(
        self,
        content: str,
        curriculum: Optional[str] = None,
        generation_prompt: Optional[str] = None
    ) -> BaseEvaluationResult:
        """
        Evaluate educational content with hierarchical decomposition.
        
        This method provides comprehensive evaluation of nested content:
        1. Classifies top-level content type
        2. Decomposes into hierarchical structure (e.g., quiz → questions)
        3. Evaluates bottom-up:
           - Children evaluated first (in parallel where possible)
           - Parents evaluated with knowledge of child results
           - All nodes receive root content as context
        4. Returns nested evaluation results
        
        Use this method for all evaluations. The method automatically handles:
        - Simple content (single question, no nesting)
        - Complex content (quizzes with questions, reading passages with quizzes)
        - Context-aware evaluation (questions aware of parent quiz/passage)
        
        Args:
            content: The educational content to evaluate (any string, may contain image URLs)
            curriculum: Curriculum to use (defaults to settings.DEFAULT_CURRICULUM)
            generation_prompt: Optional prompt used to generate the content (for AI-generated content)
            
        Returns:
            BaseEvaluationResult (Pydantic model) with evaluation results and nested subcontent_evaluations
            
        Raises:
            ValueError: If content is invalid or curriculum not supported
            RuntimeError: If evaluation fails
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")
        
        curriculum = curriculum or settings.DEFAULT_CURRICULUM
        
        start_time = time.time()
        logger.info(f"Starting evaluation with curriculum: {curriculum}")
        
        try:
            # Step 1: Classify top-level content
            logger.info("Step 1: Classifying content...")
            content_type = await self.classifier.classify(content)
            logger.info(f"Content classified as: {content_type.value}")
            
            # Step 2: Decompose into hierarchical structure
            logger.info("Step 2: Decomposing content into hierarchical structure...")
            content_tree = await self.decomposer.decompose(content, content_type)
            logger.info(
                f"Decomposition complete. "
                f"Depth: {content_tree.get_depth()}, "
                f"Total nodes: {content_tree.count_nodes()}"
            )
            
            # Step 3: Evaluate hierarchically (bottom-up)
            logger.info("Step 3: Evaluating hierarchically (bottom-up)...")
            result = await self.orchestrator.evaluate_hierarchical(
                content_tree, 
                curriculum, 
                generation_prompt
            )
            
            logger.info(
                f"Evaluation complete. "
                f"Type: {content_type.value}, "
                f"Overall: {result.overall.score:.2f}, "
                f"Subcontent evaluations: {len(result.subcontent_evaluations) if result.subcontent_evaluations else 0}"
            )
            logger.info(f"Evaluation completed in {time.time() - start_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed after {time.time() - start_time:.2f} seconds: {e}")
            raise RuntimeError(f"Evaluation failed: {e}")
    
    async def evaluate_json(
        self,
        content: str,
        curriculum: Optional[str] = None,
        generation_prompt: Optional[str] = None
    ) -> str:
        """
        Evaluate content and return JSON string.
        
        Convenience method that wraps evaluate() and returns JSON format.
        Useful for REST APIs, CLIs, and other scenarios where JSON serialization is needed.
        
        Args:
            content: The educational content to evaluate
            curriculum: Curriculum to use (defaults to settings.DEFAULT_CURRICULUM)
            generation_prompt: Optional prompt used to generate the content (for AI-generated content)
            
        Returns:
            JSON string with evaluation results
            
        Raises:
            ValueError: If content is invalid or curriculum not supported
            RuntimeError: If evaluation fails
        """
        result = await self.evaluate(content, curriculum, generation_prompt)
        return result.to_json()
