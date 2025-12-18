"""
Evaluation orchestrator for hierarchical content.

This module provides the EvaluationOrchestrator class which coordinates
bottom-up evaluation of nested educational content, ensuring that child
components are evaluated before their parents and that results propagate
appropriately.
"""

import asyncio
import logging
from typing import Dict

from openai import AsyncOpenAI

from inceptbench_new.evaluators.article import ArticleEvaluator
from inceptbench_new.evaluators.base import BaseEvaluator
from inceptbench_new.evaluators.fiction_reading import FictionReadingEvaluator
from inceptbench_new.evaluators.nonfiction_reading import NonfictionReadingEvaluator
from inceptbench_new.evaluators.other import OtherEvaluator
from inceptbench_new.evaluators.question import QuestionEvaluator
from inceptbench_new.evaluators.quiz import QuizEvaluator
from inceptbench_new.models import BaseEvaluationResult, ContentNode, ContentTree, ContentType

logger = logging.getLogger(__name__)


class EvaluationOrchestrator:
    """
    Orchestrates evaluation of hierarchical content.
    
    Coordinates bottom-up evaluation where:
    1. Leaf nodes (no children) are evaluated first
    2. Sibling nodes are evaluated in parallel
    3. Parent nodes are evaluated with knowledge of child results
    4. All nodes receive the root content as full_context
    """
    
    def __init__(self, client: AsyncOpenAI):
        """
        Initialize the evaluation orchestrator.
        
        Args:
            client: Authenticated OpenAI async client
        """
        self.evaluators: Dict[ContentType, BaseEvaluator] = {
            ContentType.QUESTION: QuestionEvaluator(),
            ContentType.QUIZ: QuizEvaluator(),
            ContentType.FICTION_READING: FictionReadingEvaluator(),
            ContentType.NONFICTION_READING: NonfictionReadingEvaluator(),
            ContentType.ARTICLE: ArticleEvaluator(),
            ContentType.OTHER: OtherEvaluator(),
        }
        logger.info("EvaluationOrchestrator initialized with all content evaluators")
    
    async def evaluate_hierarchical(
        self, 
        content_tree: ContentTree,
        curriculum: str,
        generation_prompt: str = None
    ) -> BaseEvaluationResult:
        """
        Evaluate content tree bottom-up.
        
        This method evaluates the hierarchical content structure, ensuring that:
        - Children are evaluated before their parents
        - Sibling nodes are evaluated in parallel for performance
        - Each node has access to the root content for contextual evaluation
        - Parent nodes receive child evaluation results
        
        The root content is passed as a parameter throughout evaluation,
        avoiding duplication in every node.
        
        Args:
            content_tree: The ContentTree containing root_content and root_node
            curriculum: Curriculum to use for evaluation
            generation_prompt: Optional prompt used to generate the content
            
        Returns:
            Evaluation result for the root node (with child results attached)
            
        Raises:
            RuntimeError: If evaluation fails
        """
        logger.info(
            f"Evaluating {content_tree.root_node.type.value} content tree "
            f"(depth: {content_tree.get_depth()}, nodes: {content_tree.count_nodes()})"
        )
        
        # Evaluate the tree, passing root_content and generation_prompt as parameters
        return await self._evaluate_node(
            node=content_tree.root_node,
            root_content=content_tree.root_content,
            curriculum=curriculum,
            generation_prompt=generation_prompt
        )
    
    async def _evaluate_node(
        self,
        node: ContentNode,
        root_content: str,
        curriculum: str,
        generation_prompt: str = None
    ) -> BaseEvaluationResult:
        """
        Internal method to recursively evaluate a content node.
        
        Args:
            node: The content node to evaluate
            root_content: The complete root content (for contextual evaluation)
            curriculum: Curriculum to use for evaluation
            generation_prompt: Optional prompt used to generate the content
            
        Returns:
            Evaluation result for this node (with child results attached)
        """
        logger.info(
            f"Evaluating {node.type.value} node "
            f"(children: {len(node.children)}, depth: {node.get_depth()})"
        )
        
        # Base case: Evaluate subcontent first (in parallel)
        subcontent_results = []
        if node.children:
            logger.info(f"Evaluating {len(node.children)} subcontent items in parallel...")
            
            # Create evaluation tasks for all children (pass root_content and generation_prompt through)
            subcontent_tasks = [
                self._evaluate_node(child, root_content, curriculum, generation_prompt)
                for child in node.children
            ]
            
            # Execute in parallel and gather results
            subcontent_results = await asyncio.gather(*subcontent_tasks)
            
            # Store results in nodes (for potential debugging/inspection)
            for child, result in zip(node.children, subcontent_results):
                child.evaluation_result = result
            
            logger.info(
                f"Completed evaluation of {len(subcontent_results)} subcontent items. "
                f"Average subcontent score: {sum(r.overall.score for r in subcontent_results) / len(subcontent_results):.2f}"
            )
        
        # Evaluate this node with subcontent context
        evaluator = self.evaluators.get(node.type)
        if not evaluator:
            raise RuntimeError(f"No evaluator found for content type: {node.type.value}")
        
        logger.info(f"Evaluating {node.type.value} node (content length: {len(node.extracted_content)} chars)")
        
        # Determine full_context parameter:
        # - If this node's extracted_content equals root_content, no need to pass it
        # - Otherwise, pass root_content as full_context
        full_context = None if node.extracted_content == root_content else root_content
        
        try:
            result = await evaluator.evaluate(
                content=node.extracted_content,
                curriculum=curriculum,
                full_context=full_context,
                subcontent_results=subcontent_results if subcontent_results else None,
                generation_prompt=generation_prompt
            )
            
            # Attach subcontent evaluations to result
            if subcontent_results:
                result.subcontent_evaluations = subcontent_results
            
            logger.info(
                f"Completed evaluation of {node.type.value}. "
                f"Overall score: {result.overall.score:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error evaluating {node.type.value} node: {e}")
            raise RuntimeError(f"Evaluation failed for {node.type.value}: {e}")

