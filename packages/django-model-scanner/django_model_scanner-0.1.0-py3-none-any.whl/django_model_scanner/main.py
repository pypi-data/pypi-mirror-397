#!/usr/bin/env python3
"""Command-line interface for Django Model Scanner.

This module provides a user-friendly CLI wrapper around the pylint-based
Django model scanner, simplifying invocation and providing clear options.
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple


def validate_project_path(path: str) -> Tuple[bool, Optional[str]]:
    """Validate that the project path exists and is readable.

    Args:
        path: Path to Django project to scan

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    if not os.path.exists(path):
        return False, f"Project path not found: {path}"

    if not os.access(path, os.R_OK):
        return False, f"Cannot access project path: {path}"

    return True, None


def validate_output_path(path: str) -> Tuple[bool, Optional[str]]:
    """Validate that the output path's parent directory exists and is writable.

    Args:
        path: Output file path for YAML

    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if valid
        - (False, error_message) if invalid
    """
    # Get parent directory
    parent_dir = os.path.dirname(os.path.abspath(path))

    # If no directory specified, use current directory
    if not parent_dir:
        parent_dir = "."

    if not os.path.exists(parent_dir):
        return False, f"Output directory does not exist: {parent_dir}"

    if not os.access(parent_dir, os.W_OK):
        return False, f"Output directory is not writable: {parent_dir}"

    return True, None


def run_scanner(project_path: str, output_path: str) -> int:
    """Run the Django model scanner using pylint.

    Args:
        project_path: Path to Django project to scan
        output_path: Path to write YAML output

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        from pylint.lint import Run
    except ImportError:
        print("Error: pylint is not installed. Install it with: pip install pylint", file=sys.stderr)
        return 1

    # Construct pylint arguments
    pylint_args = [
        project_path,
        "--disable=all",
        "--load-plugins=django_model_scanner.checker",
        "--enable=django-model-scanner",
        f"--django-models-output={output_path}",
    ]

    try:
        # Run pylint - it may raise SystemExit
        Run(pylint_args, exit=False)
        return 0
    except SystemExit as e:
        # Pylint uses sys.exit(), capture the code
        code = e.code if e.code else 0
        return int(code) if isinstance(code, int) else 0
    except Exception as e:
        print(f"Error running scanner: {e}", file=sys.stderr)
        return 2


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Get version from package
    try:
        from django_model_scanner import __version__
    except ImportError:
        __version__ = "unknown"

    # Create argument parser
    parser = argparse.ArgumentParser(
        prog="django-model-scanner",
        description="Static analysis tool for Django models - scan and export to YAML without code execution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan a project with default output
  %(prog)s -p /path/to/django/project
  
  # Scan with custom output location
  %(prog)s -p ./src -o models.yaml
  
  # Scan specific app
  %(prog)s -p ./myapp/models.py -o myapp_models.yaml

For more information, visit: https://github.com/yourusername/django-model-scanner
        """,
    )

    parser.add_argument(
        "-p", "--project", required=True, type=str, help="Path to Django project, app, or models.py file to scan"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="django_models.yaml",
        type=str,
        help="Output YAML file path (default: django_models.yaml)",
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    # Parse arguments
    args = parser.parse_args()

    # Validate project path
    project_valid, project_error = validate_project_path(args.project)
    if not project_valid:
        print(f"Error: {project_error}", file=sys.stderr)
        return 1

    # Validate output path
    output_valid, output_error = validate_output_path(args.output)
    if not output_valid:
        print(f"Error: {output_error}", file=sys.stderr)
        return 1

    # Run the scanner
    exit_code = run_scanner(args.project, args.output)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
