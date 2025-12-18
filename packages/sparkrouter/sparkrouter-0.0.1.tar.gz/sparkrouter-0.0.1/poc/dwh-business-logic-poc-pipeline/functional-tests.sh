#!/bin/bash
# functional-tests.sh - Run functional tests for the business logic code

set -e  # Exit on any error

export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
export PATH="$JAVA_HOME/bin:$PATH"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#TEST_DIR="${1:-$SCRIPT_DIR/tests}"
TEST_DIR="${1:-$SCRIPT_DIR/tests/functional/dwh/jobs/transform_images}"

echo "=== Running Functional Tests ==="
echo "Test Directory: $TEST_DIR"

# Source the environment setup script
if [ -f "$SCRIPT_DIR/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "$SCRIPT_DIR/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

"$SCRIPT_DIR/build-scala.sh"

CURRENT_PYTHON="$PYTHON_CMD"
echo "Functional Tests Using Python: $CURRENT_PYTHON"

# Check if pytest is available
echo "Running functional tests..."
if ! $CURRENT_PYTHON -c "import pytest" &>/dev/null; then
    echo "pytest not found. Installing..."
    $CURRENT_PYTHON -m pip install pytest
    if [ $? -ne 0 ]; then
        echo "Failed to install pytest. Cannot run tests."
        exit 1
    fi
fi

# Run pytest with the same Python interpreter (only functional tests)
$CURRENT_PYTHON -m pytest "$TEST_DIR" -v -m "functional" --cov=src --cov-report=term-missing --tb=no -q

if [ $? -eq 0 ]; then
    echo "✓ All functional tests passed"
else
    echo "✗ Functional tests failed"
    exit 1
fi

echo "=== Functional Testing completed! ==="
