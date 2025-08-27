#!/usr/bin/env python3
"""
Test runner script for the LLM Business Data Query System.

This script runs tests for both Django API and Flask LLM applications.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(command, cwd=None):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(command)}")
    if cwd:
        print(f"In directory: {cwd}")

    result = subprocess.run(command, cwd=cwd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode == 0


def setup_django_tests():
    """Set up Django test environment."""
    django_dir = Path("django_api")

    print("Setting up Django tests...")

    # Install test requirements
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"],
        cwd=django_dir,
    ):
        print("Failed to install Django test requirements")
        return False

    return True


def setup_flask_tests():
    """Set up Flask test environment."""
    flask_dir = Path("flask_llm")

    print("Setting up Flask tests...")

    # Install test requirements
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", "test_requirements.txt"],
        cwd=flask_dir,
    ):
        print("Failed to install Flask test requirements")
        return False

    return True


def run_django_tests(verbose=False):
    """Run Django tests."""
    django_dir = Path("django_api")

    print("\n" + "=" * 60)
    print("RUNNING DJANGO API TESTS")
    print("=" * 60)

    command = [sys.executable, "-m", "pytest"]
    if verbose:
        command.append("-v")

    return run_command(command, cwd=django_dir)


def run_flask_tests(verbose=False):
    """Run Flask tests."""
    flask_dir = Path("flask_llm")

    print("\n" + "=" * 60)
    print("RUNNING FLASK LLM TESTS")
    print("=" * 60)

    command = [sys.executable, "-m", "pytest"]
    if verbose:
        command.append("-v")

    return run_command(command, cwd=flask_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Run tests for LLM Business Data Query System"
    )
    parser.add_argument(
        "--django-only", action="store_true", help="Run only Django tests"
    )
    parser.add_argument(
        "--flask-only", action="store_true", help="Run only Flask tests"
    )
    parser.add_argument(
        "--setup-only", action="store_true", help="Only install test dependencies"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    success = True

    # Setup test environments
    if not args.flask_only:
        if not setup_django_tests():
            success = False

    if not args.django_only:
        if not setup_flask_tests():
            success = False

    if args.setup_only:
        return 0 if success else 1

    # Run tests
    if not args.flask_only:
        if not run_django_tests(args.verbose):
            success = False

    if not args.django_only:
        if not run_flask_tests(args.verbose):
            success = False

    print("\n" + "=" * 60)
    if success:
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 60)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
