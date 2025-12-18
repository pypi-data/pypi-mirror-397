"""
Evaluation orchestration for hierarchical content.

This package provides functionality to orchestrate bottom-up evaluation of
nested educational content, coordinating parallel evaluation of sibling nodes
and propagating context up the tree.
"""

from .evaluation_orchestrator import EvaluationOrchestrator

__all__ = ["EvaluationOrchestrator"]

