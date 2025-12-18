"""
Main entry point for the inceptbench CLI.

This allows running the CLI with:
    python -m inceptbench evaluate ...

Instead of:
    python -m inceptbench.cli evaluate ...
"""

from inceptbench.cli import cli

if __name__ == '__main__':
    cli()

