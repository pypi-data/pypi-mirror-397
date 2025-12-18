#!/bin/bash
# unit-tests.sh - Run unit tests for the business logic code

set -e  # Exit on any error

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="${1:-$SCRIPT_DIR/tests}"

echo "=== Running Unit Tests ==="
echo "Test Directory: $TEST_DIR"

# Source the environment setup script
if [ -f "$SCRIPT_DIR/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "$SCRIPT_DIR/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

# Use PYTHON_CMD from setup-env.sh instead of $(which python)
CURRENT_PYTHON="$PYTHON_CMD"
echo "Unit Tests Using Python: $CURRENT_PYTHON"

# Check if pytest is available
echo "Running unit tests..."
if ! $CURRENT_PYTHON -c "import pytest" &>/dev/null; then
    echo "pytest not found. Installing..."
#    cd "$SCRIPT_DIR" # Change to script directory to avoid FileNotFoundError
    $CURRENT_PYTHON -m pip install pytest
    if [ $? -ne 0 ]; then
        echo "Failed to install pytest. Cannot run tests."
        exit 1
    fi
fi

# Run pytest with the same Python interpreter (excluding integration tests)
$CURRENT_PYTHON -m pytest "$TEST_DIR" -v -m "not integration and not functional" --cov=src --cov-report=term-missing --tb=no -q


if [ $? -eq 0 ]; then
    echo "✓ All unit tests passed"
else
    echo "✗ Unit tests failed"
    exit 1
fi

echo "=== Unit Testing completed! ==="
