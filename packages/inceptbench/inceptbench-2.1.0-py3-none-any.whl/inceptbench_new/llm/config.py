"""
Configuration and registry for LLM model assignments.

This module centralizes all model-to-task assignments, making it easy to
experiment with different models for different roles in the system.

To change which model handles a specific task, simply edit the
LLM_TASK_REGISTRY dictionary below.
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class LLMConfig:
    """
    Configuration for a specific LLM instance.
    
    Attributes:
        provider: Provider name ("openai", "anthropic", "gemini", etc.)
        model: Model identifier (e.g., "gpt-5", "claude-sonnet-4-5")
        timeout: Request timeout in seconds
        temperature: Sampling temperature (0.0 = deterministic, 1.0 = creative)
        max_tokens: Maximum tokens in response
    """
    provider: str
    model: str
    timeout: float = 60.0
    temperature: float = 0.0
    max_tokens: int = 16384
    
    def __post_init__(self):
        """Validate configuration."""
        if self.provider not in ["openai", "anthropic", "gemini"]:
            raise ValueError(
                f"Unknown provider: {self.provider}. "
                f"Supported: openai, anthropic, gemini"
            )
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {self.timeout}")
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError(f"Temperature must be in [0.0, 2.0], got {self.temperature}")
        if self.max_tokens <= 0:
            raise ValueError(f"max_tokens must be positive, got {self.max_tokens}")


# =============================================================================
# TASK REGISTRY - Single source of truth for model assignments
# =============================================================================
#
# This is the ONLY place you need to edit to change which model handles
# which task. All other code uses these assignments automatically.
#
# To experiment with different models:
# 1. Change the provider and/or model for any task
# 2. Adjust timeout/temperature as needed
# 3. Test - no other code changes required!
#
# =============================================================================

LLM_TASK_REGISTRY: Dict[str, LLMConfig] = {
    # Content Classification
    # Determines the type of educational content (question, quiz, passage, etc.)
    "classifier": LLMConfig(
        provider="openai",
        model="gpt-5",
        timeout=30.0
    ),
    
    # Content Decomposition
    # Breaks down hierarchical content (e.g., quiz -> questions)
    "decomposer": LLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-5",
        timeout=60.0,
        temperature=0.0
    ),
    
    # Content Evaluation
    # Main evaluator for all content types
    "evaluator": LLMConfig(
        provider="openai",
        model="gpt-5",
        timeout=120.0
    ),
    
    # Answer Choice Extraction (Quiz)
    # Extracts correct/incorrect answer patterns from quizzes
    "answer_extractor": LLMConfig(
        provider="openai",
        model="gpt-5",
        timeout=60.0
    ),
    
    # Curriculum Standards Extraction
    # Identifies explicit curriculum standards in content
    "curriculum_extractor": LLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-5",
        timeout=30.0,
        temperature=0.0
    ),
    
    # Curriculum Standards Deduplication
    # Removes duplicate curriculum standards from search results
    "curriculum_deduplicator": LLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-5",
        timeout=60.0,
        temperature=0.0
    ),
    
    # Object Counting (Vision)
    # Counts objects in images for educational content validation
    "object_counter": LLMConfig(
        provider="anthropic",
        model="claude-sonnet-4-5",
        timeout=120.0,
        temperature=0.0,
        max_tokens=16384
    ),
}


def get_llm_config(task: str) -> LLMConfig:
    """
    Get the LLM configuration for a specific task.
    
    Args:
        task: Task name from LLM_TASK_REGISTRY
        
    Returns:
        LLMConfig for the specified task
        
    Raises:
        ValueError: If task is not registered
        
    Example:
        config = get_llm_config("classifier")
        print(f"Classifier uses {config.provider}/{config.model}")
    """
    if task not in LLM_TASK_REGISTRY:
        available = ", ".join(sorted(LLM_TASK_REGISTRY.keys()))
        raise ValueError(
            f"Unknown task: '{task}'. "
            f"Available tasks: {available}"
        )
    return LLM_TASK_REGISTRY[task]


def list_tasks() -> list[str]:
    """
    Get list of all registered tasks.
    
    Returns:
        Sorted list of task names
    """
    return sorted(LLM_TASK_REGISTRY.keys())


def get_task_info(task: str) -> str:
    """
    Get human-readable information about a task's model assignment.
    
    Args:
        task: Task name
        
    Returns:
        Formatted string describing the assignment
        
    Example:
        >>> print(get_task_info("classifier"))
        classifier: openai/gpt-5 (timeout: 30.0s, temp: 0.0)
    """
    config = get_llm_config(task)
    return (
        f"{task}: {config.provider}/{config.model} "
        f"(timeout: {config.timeout}s, temp: {config.temperature})"
    )

