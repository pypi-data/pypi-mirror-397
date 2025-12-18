"""
Content decomposer for hierarchical educational content.

This module provides the ContentDecomposer class which uses LLM-based analysis
to identify and extract nested content structures (e.g., questions within quizzes,
quizzes within reading passages).
"""

import logging
import time
from pathlib import Path
from typing import Optional

from inceptbench_new.llm import LLMFactory, LLMMessage
from inceptbench_new.models import ContentNode, ContentTree, ContentType, DecompositionResult

logger = logging.getLogger(__name__)


class ContentDecomposer:
    """
    Decomposes educational content into hierarchical tree structure.
    
    Uses content-type-specific decomposition prompts to identify nested
    components. For example:
    - Quiz → individual questions
    - Reading passage → quizzes and/or questions
    
    The decomposition logic is driven by prompts in src/prompts/<content_type>/decomposition.txt
    If no decomposition prompt exists, the content is treated as a leaf node.
    """
    
    def __init__(self):
        """Initialize the content decomposer."""
        self.llm = LLMFactory.create("decomposer")
    
    def _get_decomposition_prompt_path(self, content_type: ContentType) -> Optional[Path]:
        """
        Get the path to the decomposition prompt for a content type.
        
        Args:
            content_type: Type of content to decompose
            
        Returns:
            Path to decomposition prompt, or None if decomposition not supported
        """
        # Map content type to directory name
        type_map = {
            ContentType.QUESTION: "question",
            ContentType.QUIZ: "quiz",
            ContentType.FICTION_READING: "fiction_reading",
            ContentType.NONFICTION_READING: "nonfiction_reading",
            ContentType.ARTICLE: "article",
            ContentType.OTHER: "other",
        }
        
        dir_name = type_map.get(content_type)
        if not dir_name:
            return None
        
        prompt_path = Path(__file__).parent.parent / "prompts" / dir_name / "decomposition.txt"
        
        # Only return path if file exists
        return prompt_path if prompt_path.exists() else None
    
    def _load_decomposition_prompt(self, content_type: ContentType) -> Optional[str]:
        """
        Load the decomposition prompt for a content type.
        
        Args:
            content_type: Type of content to decompose
            
        Returns:
            Decomposition prompt text, or None if decomposition not supported
        """
        prompt_path = self._get_decomposition_prompt_path(content_type)
        
        if prompt_path is None:
            logger.debug(f"No decomposition prompt for {content_type.value}")
            return None
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Error loading decomposition prompt for {content_type.value}: {e}")
            return None
    
    async def _call_decomposer_llm(
        self, 
        content: str, 
        prompt: str
    ) -> DecompositionResult:
        """
        Call LLM to decompose content into components.
        
        Args:
            content: Content to decompose
            prompt: Decomposition prompt (content-type-specific)
            
        Returns:
            DecompositionResult with extracted children
        """
        try:
            result = await self.llm.generate_structured(
                messages=[
                    LLMMessage(role="system", content=prompt),
                    LLMMessage(role="user", content=f"Analyze this content:\n\n{content}")
                ],
                response_schema=DecompositionResult
            )
            return result
            
        except Exception as e:
            logger.error(f"Error calling decomposer LLM: {e}")
            # On error, treat as leaf node
            return DecompositionResult(has_children=False, children=[])
    
    async def decompose(
        self, 
        content: str, 
        content_type: ContentType
    ) -> ContentTree:
        """
        Decompose content into hierarchical tree structure.
        
        This method recursively decomposes content, identifying nested components
        and building a tree structure. The root content is stored once in the
        ContentTree to avoid duplication across all nodes.
        
        Args:
            content: The content to decompose
            content_type: The type of this content
            
        Returns:
            ContentTree with root_content and decomposed node structure
        """
        logger.info(f"Decomposing {content_type.value} content ({len(content)} chars)")
        
        # Decompose into node structure
        root_node = await self._decompose_node(content, content_type)
        
        # Wrap in ContentTree to store root_content once
        return ContentTree(
            root_content=content,
            root_node=root_node
        )
    
    async def _decompose_node(
        self,
        content: str,
        content_type: ContentType
    ) -> ContentNode:
        """
        Internal method to recursively decompose a content node.
        
        This builds the tree structure without storing root_content in each node.
        
        Args:
            content: The content to decompose for this node
            content_type: The type of this content
            
        Returns:
            ContentNode with children (if any)
        """

        start_time = time.time()

        # Load decomposition prompt for this content type
        decomposition_prompt = self._load_decomposition_prompt(content_type)
        
        # If no decomposition prompt, treat as leaf node
        if decomposition_prompt is None:
            logger.debug(f"No decomposition for {content_type.value}, treating as leaf")
            return ContentNode(
                type=content_type,
                extracted_content=content,
                children=[]
            )
        
        # Call LLM to extract structure
        try:
            decomposition_result = await self._call_decomposer_llm(content, decomposition_prompt)
        except Exception as e:
            logger.error(
                f"Decomposition failed after {time.time() - start_time:.2f}s for {content_type.value}: {e}"
            )
            # Fallback to leaf node on error
            return ContentNode(
                type=content_type,
                extracted_content=content,
                children=[]
            )
        
        # If no children found, return leaf node
        if not decomposition_result.has_children or not decomposition_result.children:
            logger.debug(
                f"No children found in {content_type.value} after {time.time() - start_time:.2f}s"
            )
            return ContentNode(
                type=content_type,
                extracted_content=content,
                children=[]
            )
        
        # Recursively decompose children
        child_nodes = []
        for extracted_child in decomposition_result.children:
            logger.info(
                f"Decomposing child: {extracted_child.type.value} "
                f"after {time.time() - start_time:.2f}s"
                f"({len(extracted_child.extracted_content)} chars)"
            )
            
            # Validate that extracted content exists in original (verbatim extraction check)
            if extracted_child.extracted_content not in content:
                logger.warning(
                    f"Extracted {extracted_child.type.value} content not found verbatim in parent. "
                    f"LLM may have paraphrased instead of extracting exactly. "
                    f"This could affect evaluation accuracy."
                )
                logger.warning(f"Extracted content: {extracted_child.extracted_content}")
                logger.warning(f"Parent content: {content}")
            
            # Recursively decompose this child
            child_node = await self._decompose_node(
                content=extracted_child.extracted_content,
                content_type=extracted_child.type
            )
            
            child_nodes.append(child_node)
        
        # Create parent node with children
        parent_node = ContentNode(
            type=content_type,
            extracted_content=content,
            children=child_nodes
        )
        
        logger.info(
            f"Decomposed {content_type.value} into {len(child_nodes)} "
            f"children in {time.time() - start_time:.2f}s "
            f"(depth: {parent_node.get_depth()}, total nodes: {parent_node.count_nodes()})"
        )
        
        return parent_node

