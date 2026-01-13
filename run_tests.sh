#!/bin/bash
# Simple test runner for OPGG.py

TARGET="${1:-all}"

case "$TARGET" in
    all)
        echo "Running all tests..."
        py -m pytest tests/ -v
        ;;
    unit)
        echo "Running unit tests..."
        py -m pytest tests/unit/ -v
        ;;
    integration)
        echo "Running integration tests..."
        py -m pytest tests/integration/ -v
        ;;
    quick)
        echo "Running all tests (short output)..."
        py -m pytest tests/ -v --tb=line
        ;;
    failed)
        echo "Re-running last failed tests..."
        py -m pytest tests/ -v --lf
        ;;
    coverage)
        echo "Running tests with coverage..."
        py -m pytest tests/ --cov=opgg --cov-report=html
        ;;
    help)
        echo ""
        echo "Available test targets:"
        echo "  all         - Run all tests (default)"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  quick       - Run all tests with short output"
        echo "  failed      - Re-run last failed tests"
        echo "  coverage    - Run tests with coverage report"
        echo ""
        echo "Usage: ./test.sh [target]"
        echo "Example: ./test.sh unit"
        ;;
    *)
        echo "Unknown target: $TARGET"
        echo "Run './test.sh help' for available targets"
        exit 1
        ;;
esac
