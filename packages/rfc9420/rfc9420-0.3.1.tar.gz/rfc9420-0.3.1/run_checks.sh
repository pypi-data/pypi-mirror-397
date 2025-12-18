#!/bin/bash
# Script to run mypy, ruff, and pytest checks
# Outputs results to mypy_output.txt, ruff_output.txt, and test_output.txt

echo "Running type checks with mypy..."
uv run mypy src > mypy_output.txt 2>&1
MYPY_EXIT=$?

echo "Running linting with ruff..."
uv run ruff check . > ruff_output.txt 2>&1
RUFF_EXIT=$?

echo "Running tests with pytest..."
uv run pytest -v > test_output.txt 2>&1
PYTEST_EXIT=$?

echo ""
echo "Results:"
echo "  mypy:   mypy_output.txt (exit code: $MYPY_EXIT)"
echo "  ruff:   ruff_output.txt (exit code: $RUFF_EXIT)"
echo "  pytest: test_output.txt (exit code: $PYTEST_EXIT)"

TOTAL_EXIT=$((MYPY_EXIT + RUFF_EXIT + PYTEST_EXIT))
if [ $TOTAL_EXIT -eq 0 ]; then
    echo ""
    echo "All checks passed!"
    exit 0
else
    echo ""
    echo "Some checks failed. Check the output files for details."
    exit 1
fi

