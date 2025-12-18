"""
Command-line interface for educational content evaluator.

This module provides a CLI for testing the evaluation system.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Optional

from .service import EvaluationService
from .config.settings import settings


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


async def evaluate_content(
    content: str,
    curriculum: str,
    output_file: Optional[Path],
    verbose: bool,
    generation_prompt: Optional[str] = None
) -> int:
    """
    Evaluate content and output results.
    
    Args:
        content: Content to evaluate
        curriculum: Curriculum to use
        output_file: Optional file path to save output
        verbose: Whether to show verbose output
        generation_prompt: Optional prompt used to generate the content
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    try:
        service = EvaluationService()
        
        print(f"\nEvaluating content using curriculum: {curriculum}")
        if generation_prompt:
            print(f"Using generation prompt: {generation_prompt[:100]}...")
        print("-" * 80)
        
        # Evaluate content (returns JSON for easy display)
        result_json = await service.evaluate_json(content, curriculum, generation_prompt)
        
        # Parse for display
        result_dict = json.loads(result_json)
        
        print("\n✓ Evaluation complete!")
        print(f"  Content Type: {result_dict.get('content_type', 'unknown')}")
        print(f"  Overall Score: {result_dict.get('overall', {}).get('score', 0):.2f}")
        print(f"  Factual Accuracy: {result_dict.get('factual_accuracy', {}).get('score', 0):.1f}")
        print(f"  Educational Accuracy: {result_dict.get('educational_accuracy', {}).get('score', 0):.1f}")
        
        # Show child evaluations count if present
        if result_dict.get('subcontent_evaluations'):
            print(f"  Nested Evaluations: {len(result_dict['subcontent_evaluations'])}")
        
        # Save to file if requested
        if output_file:
            output_file.write_text(result_json)
            print(f"\n✓ Results saved to: {output_file}")
        
        # Show full results if verbose
        if verbose:
            print("\n" + "=" * 80)
            print("FULL EVALUATION RESULTS")
            print("=" * 80)
            print(json.dumps(result_dict, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Evaluation failed: {e}", file=sys.stderr)
        if verbose:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Evaluate educational content quality",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate a string
  python -m inceptbench_new.cli "What is 2+2?"
  
  # Evaluate content from a file
  python -m inceptbench_new.cli --file question.txt
  
  # Use a different curriculum
  python -m inceptbench_new.cli --curriculum common_core --file quiz.txt
  
  # Include generation prompt as string (for AI-generated content)
  python -m inceptbench_new.cli --file question.txt --generation-prompt "Create a math question for 5th grade"
  
  # Include generation prompt from file (for longer prompts)
  python -m inceptbench_new.cli --file question.txt --generation-prompt-file prompt.txt
  
  # Save results to file
  python -m inceptbench_new.cli --file content.txt --output results.json
  
  # Verbose output with debug logging
  python -m inceptbench_new.cli --file content.txt --verbose
        """
    )
    
    # Content input (mutually exclusive)
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "content",
        nargs="?",
        help="Educational content to evaluate (as string)"
    )
    input_group.add_argument(
        "-f", "--file",
        type=Path,
        help="File containing content to evaluate"
    )
    
    # Options
    parser.add_argument(
        "-c", "--curriculum",
        default=settings.DEFAULT_CURRICULUM,
        help=f"Curriculum to use for evaluation (default: {settings.DEFAULT_CURRICULUM})"
    )
    
    # Generation prompt (mutually exclusive)
    prompt_group = parser.add_mutually_exclusive_group()
    prompt_group.add_argument(
        "-g", "--generation-prompt",
        type=str,
        help="Prompt used to generate the content (for AI-generated content evaluation)"
    )
    prompt_group.add_argument(
        "--generation-prompt-file",
        type=Path,
        help="File containing the generation prompt"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="File to save evaluation results (JSON format)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show verbose output and debug logging"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Get content
    if args.file:
        if not args.file.exists():
            print(f"Error: File not found: {args.file}", file=sys.stderr)
            return 1
        try:
            content = args.file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading file: {e}", file=sys.stderr)
            return 1
    else:
        content = args.content
    
    if not content.strip():
        print("Error: Content cannot be empty", file=sys.stderr)
        return 1
    
    # Get generation prompt (from string or file)
    generation_prompt = None
    if args.generation_prompt:
        generation_prompt = args.generation_prompt
    elif args.generation_prompt_file:
        if not args.generation_prompt_file.exists():
            print(f"Error: Generation prompt file not found: {args.generation_prompt_file}", file=sys.stderr)
            return 1
        try:
            generation_prompt = args.generation_prompt_file.read_text(encoding='utf-8')
        except Exception as e:
            print(f"Error reading generation prompt file: {e}", file=sys.stderr)
            return 1
    
    # Run evaluation
    exit_code = asyncio.run(evaluate_content(
        content=content,
        curriculum=args.curriculum,
        output_file=args.output,
        verbose=args.verbose,
        generation_prompt=generation_prompt
    ))
    
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

