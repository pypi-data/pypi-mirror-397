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

# Create a directory for Airflow files if it doesn't exist
PROJECT_ROOT="${SCRIPT_DIR}"
AIRFLOW_DIR="${PROJECT_ROOT}/.airflow"
mkdir -p "${AIRFLOW_DIR}"
export AIRFLOW__CORE__LOAD_EXAMPLES=False

# Set Airflow to use SQLite with a project-specific DB path
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="sqlite:///${AIRFLOW_DIR}/airflow_test.db"
# Keep the old one for backward compatibility
export AIRFLOW__CORE__SQL_ALCHEMY_CONN="sqlite:///${AIRFLOW_DIR}/airflow_test.db"

# Initialize the test database
$PYTHON_CMD -c "from airflow.utils.db import resetdb; resetdb()"

# Check if pytest is available
echo "Running unit tests..."
if ! $CURRENT_PYTHON -c "import pytest" &>/dev/null; then
    echo "pytest not found. Installing..."
    $CURRENT_PYTHON -m pip install pytest
    if [ $? -ne 0 ]; then
        echo "Failed to install pytest. Cannot run tests."
        exit 1
    fi
fi

# Run pytest with the same Python interpreter (excluding integration tests)
$CURRENT_PYTHON -m pytest "$TEST_DIR" -m "not integration and not functional" --cov=src --cov-report=term --cov-report=html --cov-branch -vv


if [ $? -eq 0 ]; then
    echo "✓ All unit tests passed"
else
    echo "✗ Unit tests failed"
    exit 1
fi

echo "=== Unit Testing completed! ==="