"""
Content tree models for hierarchical content evaluation.

This module defines data structures for representing and evaluating
nested educational content (e.g., reading passages containing quizzes
containing questions).
"""

from typing import List, Optional

from pydantic import BaseModel, Field, PrivateAttr

from .base import BaseEvaluationResult, ContentType


class ContentNode(BaseModel):
    """
    Represents a node in the hierarchical content structure.
    
    Each node represents a piece of content that can be evaluated,
    potentially containing child content nodes.
    
    Note: root_content is NOT stored here to avoid duplication across
    all nodes in the tree. It's stored once in ContentTree and passed
    as a parameter during evaluation.
    """
    
    type: ContentType = Field(
        ...,
        description="The type of this content node"
    )
    
    extracted_content: str = Field(
        ...,
        description="The extracted content for this specific node"
    )
    
    children: List['ContentNode'] = Field(
        default_factory=list,
        description="Child content nodes (e.g., questions within a quiz)"
    )
    
    evaluation_result: Optional[BaseEvaluationResult] = Field(
        None,
        description="Evaluation result for this node (populated during evaluation)"
    )
    
    # Private cached values (not included in serialization)
    _cached_depth: Optional[int] = PrivateAttr(default=None)
    _cached_node_count: Optional[int] = PrivateAttr(default=None)
    
    def is_leaf(self) -> bool:
        """Check if this is a leaf node (no children)."""
        return len(self.children) == 0
    
    def get_depth(self) -> int:
        """
        Get the depth of this tree (0 for leaf, 1+ for parents).
        
        Result is cached to avoid redundant calculations.
        """
        if self._cached_depth is None:
            if self.is_leaf():
                self._cached_depth = 0
            else:
                self._cached_depth = 1 + max(child.get_depth() for child in self.children)
        return self._cached_depth
    
    def count_nodes(self) -> int:
        """
        Count total nodes in this tree.
        
        Result is cached to avoid redundant calculations.
        """
        if self._cached_node_count is None:
            self._cached_node_count = 1 + sum(child.count_nodes() for child in self.children)
        return self._cached_node_count


class ContentTree(BaseModel):
    """
    Represents the complete hierarchical content structure.
    
    This wrapper stores the root content once (avoiding duplication) and
    provides the decomposed tree structure.
    """
    
    root_content: str = Field(
        ...,
        description="The complete original content (stored once for entire tree)"
    )
    
    root_node: ContentNode = Field(
        ...,
        description="The root node of the decomposed content tree"
    )
    
    # Private cached values (not included in serialization)
    _cached_depth: Optional[int] = PrivateAttr(default=None)
    _cached_node_count: Optional[int] = PrivateAttr(default=None)
    
    def get_depth(self) -> int:
        """
        Get the depth of the content tree.
        
        Result is cached to avoid redundant calculations.
        """
        if self._cached_depth is None:
            self._cached_depth = self.root_node.get_depth()
        return self._cached_depth
    
    def count_nodes(self) -> int:
        """
        Count total nodes in the tree.
        
        Result is cached to avoid redundant calculations.
        """
        if self._cached_node_count is None:
            self._cached_node_count = self.root_node.count_nodes()
        return self._cached_node_count


class DecompositionResult(BaseModel):
    """
    Result from content decomposition.
    
    Returned by the LLM when asked to identify nested content.
    """
    
    has_children: bool = Field(
        ...,
        description="Whether this content contains nested components"
    )
    
    children: List['ExtractedContent'] = Field(
        default_factory=list,
        description="List of extracted child content pieces"
    )


class ExtractedContent(BaseModel):
    """
    A piece of content extracted from a parent.
    
    Used during decomposition to identify nested content.
    """
    
    type: ContentType = Field(
        ...,
        description="The classified type of this extracted content"
    )
    
    extracted_content: str = Field(
        ...,
        description="The extracted content text"
    )
    
    description: Optional[str] = Field(
        None,
        description="Brief description of this content (e.g., 'Question 1: Multiple choice')"
    )

