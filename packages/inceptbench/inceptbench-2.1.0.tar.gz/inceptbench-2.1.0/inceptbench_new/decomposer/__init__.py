"""
Content decomposer for hierarchical educational content.

This package provides functionality to decompose nested educational content
(e.g., reading passages containing quizzes containing questions) into a tree
structure for bottom-up evaluation.
"""

from .content_decomposer import ContentDecomposer

__all__ = ["ContentDecomposer"]

