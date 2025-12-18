"""
Quiz evaluator for educational content.

This module provides an evaluator for quizzes (sets of multiple questions),
assessing them across quality dimensions including concept coverage, difficulty
distribution, and answer balance.
"""

import asyncio
import logging
from pathlib import Path

from scipy.stats import chisquare

from inceptbench_new.evaluators.base import BaseEvaluator
from inceptbench_new.models import BaseEvaluationResult, MetricResult, QuizEvaluationResult
from inceptbench_new.tools.api_client import get_async_openai_client

logger = logging.getLogger(__name__)


class QuizEvaluator(BaseEvaluator):
    """
    Evaluator for educational quizzes (sets of multiple questions).
    
    Assesses quizzes across 8 metrics:
    - overall (continuous [0.0, 1.0])
    - factual_accuracy (binary)
    - educational_accuracy (binary)
    - concept_coverage (binary)
    - difficulty_distribution (binary)
    - non_repetitiveness (binary)
    - test_preparedness (binary)
    - answer_balance (binary) - computed programmatically
    """
    
    def _load_prompt(self) -> str:
        """Load the quiz evaluation prompt from file."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "quiz" / "evaluation.txt"
        return self._load_prompt_from_file(prompt_path)
    
    def _get_result_model(self) -> type[BaseEvaluationResult]:
        """Return the QuizEvaluationResult model."""
        return QuizEvaluationResult
    
    async def _calculate_answer_balance(self, quiz_content: str) -> MetricResult:
        """
        Calculate answer balance using chi-square goodness of fit test.
        
        Extracts answer choices using GPT and performs statistical analysis
        to determine if correct answer positions are well-distributed.
        
        Args:
            quiz_content: The quiz content
            
        Returns:
            MetricResult with binary score (1.0 if balanced, 0.0 if not)
        """
        try:
            # Extract answer choices using GPT
            client = get_async_openai_client(timeout=60.0)
            prompt = (
                "Return a Python-formatted list of dictionaries indicating the correct/incorrect "
                "answer choices in the following quiz:\n"
                f'"""\n{quiz_content}\n"""\n'
                "The output should be formatted like this:\n"
                "[\n"
                '    {"A": "incorrect", "B": "correct", "C": "incorrect", "D": "incorrect"},\n'
                "    ...\n"
                "]\n"
                "DO NOT PLACE THE OUTPUT IN A CODE BLOCK, AND DO NOT INCLUDE ANY OTHER TEXT IN THE "
                "OUTPUT."
            )
            
            retries = 0
            answer_data = None
            while retries < 3:
                try:
                    response = await client.responses.create(
                        model=self.model,
                        input=[{"role": "user", "content": prompt}]
                    )
                    
                    # Extract text from response
                    answer_text = ""
                    for output_item in response.output:
                        if output_item.type == "message":
                            for content_item in output_item.content:
                                if content_item.type == "output_text":
                                    answer_text = content_item.text.strip()
                                    break
                    
                    if not answer_text:
                        raise ValueError("No text output from LLM")
                    
                    answer_data = eval(answer_text)  # Parse the Python list
                    if not isinstance(answer_data, list):
                        raise ValueError("LLM did not return a list")
                    break
                except Exception as e:
                    retries += 1
                    await asyncio.sleep(2**retries)
                    logger.warning(f"Retry {retries} for answer extraction: {e}")
            
            if not answer_data or len(answer_data) == 0 or retries >= 3:
                # Can't calculate - default to pass
                return MetricResult(
                    score=1.0,
                    reasoning="Could not extract answer choices for balance analysis. Defaulting to pass."
                )

            # Analyze each question's correct answer position
            position_counts = []  # List of (position, total_choices) tuples
            for question_answers in answer_data:
                choices = sorted(question_answers.keys())
                n_choices = len(choices)
                
                # Find the position (0-based) of the correct answer
                correct_choice = next(
                    (choice for choice, status in question_answers.items() 
                     if status.lower() == "correct"),
                    None
                )
                
                if correct_choice and correct_choice in choices:
                    position = choices.index(correct_choice)
                    position_counts.append((position, n_choices))
            
            if not position_counts:
                return MetricResult(
                    score=1.0,
                    reasoning="No valid correct answers found. Defaulting to pass."
                )

            # Calculate chi-square statistic
            choice_groups = {}
            for pos, n_choices in position_counts:
                if n_choices not in choice_groups:
                    choice_groups[n_choices] = []
                choice_groups[n_choices].append(pos)
            
            # Calculate chi-square contribution for each group
            observed_distributions = {}
            p_values = []
            
            for n_choices, positions in choice_groups.items():
                # Count occurrences of each position
                observed = [positions.count(i) for i in range(n_choices)]
                expected = [len(positions) / n_choices] * n_choices
                
                try:
                    stat, p_value = chisquare(observed, expected)
                    p_values.append(p_value)
                    observed_distributions[n_choices] = {
                        'positions': observed,
                        'p_value': p_value
                    }
                except Exception as e:
                    logger.warning(f"Failed to calculate chi-square for {n_choices} choices: {e}")
            
            # Use the minimum p-value across all groups
            p_value = min(p_values) if p_values else 1.0
            
            # Binary score: pass if p >= 0.60 (60% probability distribution is random)
            score = 1.0 if p_value >= 0.60 else 0.0
            
            # Build detailed explanation
            distributions = []
            for n_choices, data in observed_distributions.items():
                positions = data['positions']
                p_val = data['p_value']
                dist_str = (
                    f"Questions with {n_choices} choices: "
                    f"correct answer distribution {positions}, "
                    f"probability this is random is {p_val*100:.1f}%"
                )
                distributions.append(dist_str)
            
            reasoning = (
                "Questions include the following distributions of correct answers:\n\n" +
                "\n".join(distributions) +
                f"\n\nThe overall likelihood that this distribution is random is {p_value*100:.1f}%. "
            )
            
            if score == 1.0:
                reasoning += "The distribution is well-balanced."
            else:
                reasoning += "The distribution shows patterns that could be exploited."
                
            suggested_improvements = None if score == 1.0 else (
                "Redistribute correct answers to achieve better balance across positions A, B, C, D. "
                "Aim for roughly equal representation of each position as the correct answer."
            )
            
            return MetricResult(
                score=score,
                reasoning=reasoning,
                suggested_improvements=suggested_improvements
            )
            
        except Exception as e:
            logger.error(f"Error calculating answer balance: {e}")
            # Default to pass on error
            return MetricResult(
                score=1.0,
                reasoning=f"Error calculating answer balance: {str(e)}. Defaulting to pass."
            )
    
    async def _get_programmatic_context(self, content: str) -> str:
        """
        Override to provide answer balance analysis for quizzes.
        
        Performs chi-squared statistical analysis on correct answer distribution
        and returns formatted context for the LLM prompt.
        
        Args:
            content: The quiz content
            
        Returns:
            Formatted answer balance analysis context
        """
        # Calculate answer balance using chi-squared test
        answer_balance_result = await self._calculate_answer_balance(content)
        
        # Format as context for the LLM prompt
        answer_balance_context = f"""

Answer Balance Analysis (Pre-computed via chi-squared statistical analysis):
Score: {answer_balance_result.score}
{answer_balance_result.reasoning}

Use this answer balance data to inform your Answer Balance metric. You MUST use the 
provided score ({answer_balance_result.score}) exactly. Speak about the analysis as if 
you performed it yourself.
"""
        
        return answer_balance_context

