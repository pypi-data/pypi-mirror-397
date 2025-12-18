"""
Main entry point for the Educational Content Evaluator.

This module provides the primary entry point that can be used by CLI or API.
"""

import sys
from .cli import main as cli_main


def main():
    """Main entry point - delegates to CLI by default."""
    return cli_main()


if __name__ == "__main__":
    sys.exit(main())

