#!/usr/bin/env python3
"""Simple test runner script for OPGG.py"""

import sys
import subprocess


def run_command(cmd, description):
    """Run a command and print the result."""
    print(f"\n{'='*60}")
    print(f"  {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, shell=True)
    return result.returncode


def main():
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "all"

    commands = {
        "all": ("py -m pytest tests/ -v", "Running all tests"),
        "unit": ("py -m pytest tests/unit/ -v", "Running unit tests"),
        "integration": ("py -m pytest tests/integration/ -v", "Running integration tests"),
        "quick": ("py -m pytest tests/ -v --tb=line", "Running all tests (short output)"),
        "failed": ("py -m pytest tests/ -v --lf", "Re-running last failed tests"),
        "coverage": ("py -m pytest tests/ --cov=opgg --cov-report=html", "Running tests with coverage"),
    }

    if target == "help":
        print("\nAvailable test targets:")
        print("  all         - Run all tests (default)")
        print("  unit        - Run unit tests only")
        print("  integration - Run integration tests only")
        print("  quick       - Run all tests with short output")
        print("  failed      - Re-run last failed tests")
        print("  coverage    - Run tests with coverage report")
        print("\nUsage: python run_tests.py [target]")
        print("Example: python run_tests.py unit")
        return 0

    if target not in commands:
        print(f"Unknown target: {target}")
        print("Run 'python run_tests.py help' for available targets")
        return 1

    cmd, description = commands[target]
    return run_command(cmd, description)


if __name__ == "__main__":
    sys.exit(main())
