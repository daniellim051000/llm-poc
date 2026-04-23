#!/usr/bin/env python3
"""
Test runner for Ricoh MCP Server
Run comprehensive tests for all components
"""

import subprocess
import sys
from pathlib import Path


def run_tests(verbose: bool = False, coverage: bool = False):
    """Run the test suite"""

    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    if script_dir.name != "mcp_server":
        print("Error: This script must be run from the mcp_server directory")
        return 1

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])

    # Add test directory
    cmd.append("tests/")

    print(f"Running command: {' '.join(cmd)}")
    print("-" * 50)

    try:
        result = subprocess.run(cmd, cwd=script_dir)
        return result.returncode
    except FileNotFoundError:
        print("Error: pytest not found. Please install it with:")
        print("  pip install pytest pytest-asyncio pytest-mock")
        if coverage:
            print("  pip install coverage")
        return 1


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Run Ricoh MCP Server tests")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose test output"
    )
    parser.add_argument(
        "-c", "--coverage", action="store_true", help="Run with coverage analysis"
    )
    parser.add_argument(
        "--install-deps", action="store_true", help="Install test dependencies"
    )

    args = parser.parse_args()

    if args.install_deps:
        print("Installing test dependencies...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "pytest",
                "pytest-asyncio",
                "pytest-mock",
                "coverage",
            ]
        )
        print("Dependencies installed.")
        return 0

    return run_tests(verbose=args.verbose, coverage=args.coverage)


if __name__ == "__main__":
    exit(main())
