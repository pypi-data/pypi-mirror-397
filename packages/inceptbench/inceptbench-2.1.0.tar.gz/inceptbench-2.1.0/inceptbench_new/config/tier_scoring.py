"""
Tier-weighted scoring for evaluation metrics.

Metrics are weighted by importance:
- Tier 3 (Critical): Failures mean content is fundamentally broken
- Tier 2 (Important): Quality issues that significantly impact learning
- Tier 1 (Enhancement): Nice to have, but not deal-breakers
"""

from typing import Dict, Optional
from enum import IntEnum


class Tier(IntEnum):
    """Metric importance tiers with associated weights."""
    ENHANCEMENT = 1  # 1.0x - Nice to have
    IMPORTANT = 2    # 1.5x - Significant impact
    CRITICAL = 3     # 2.0x - Fundamental correctness


# Weight multipliers for each tier
TIER_WEIGHTS = {
    Tier.ENHANCEMENT: 1.0,
    Tier.IMPORTANT: 1.5,
    Tier.CRITICAL: 2.0,
}

# Metric tier assignments
METRIC_TIERS: Dict[str, Tier] = {
    # Critical - Wrong = unusable content
    "factual_accuracy": Tier.CRITICAL,
    "educational_accuracy": Tier.CRITICAL,

    # Important - Significantly impacts learning
    "curriculum_alignment": Tier.IMPORTANT,
    "clarity_precision": Tier.IMPORTANT,
    "reveals_misconceptions": Tier.IMPORTANT,
    "distractor_quality": Tier.IMPORTANT,
    "stimulus_quality": Tier.IMPORTANT,
    "teaching_quality": Tier.IMPORTANT,
    "worked_examples": Tier.IMPORTANT,
    "practice_problems": Tier.IMPORTANT,
    "follows_direct_instruction": Tier.IMPORTANT,
    "question_quality": Tier.IMPORTANT,
    "accuracy_logic": Tier.IMPORTANT,

    # Enhancement - Nice to have
    "localization_quality": Tier.ENHANCEMENT,
    "engagement": Tier.ENHANCEMENT,
    "difficulty_alignment": Tier.ENHANCEMENT,
    "passage_reference": Tier.ENHANCEMENT,
    "mastery_learning_alignment": Tier.ENHANCEMENT,
    "length_appropriateness": Tier.ENHANCEMENT,
    "topic_focus": Tier.ENHANCEMENT,
    "reading_level_match": Tier.ENHANCEMENT,
    "diction_and_sentence_structure": Tier.ENHANCEMENT,
}


def get_metric_weight(metric_name: str) -> float:
    """Get the weight for a metric based on its tier."""
    tier = METRIC_TIERS.get(metric_name, Tier.ENHANCEMENT)
    return TIER_WEIGHTS[tier]


def calculate_weighted_score(metric_scores: Dict[str, Optional[float]]) -> Optional[float]:
    """
    Calculate tier-weighted average from metric scores.

    Args:
        metric_scores: Dict mapping metric names to scores (0.0-1.0)

    Returns:
        Weighted average score, or None if no valid scores
    """
    if not metric_scores:
        return None

    weighted_sum = 0.0
    total_weight = 0.0

    for metric, score in metric_scores.items():
        if score is None:
            continue
        weight = get_metric_weight(metric)
        weighted_sum += score * weight
        total_weight += weight

    return weighted_sum / total_weight if total_weight > 0 else None

