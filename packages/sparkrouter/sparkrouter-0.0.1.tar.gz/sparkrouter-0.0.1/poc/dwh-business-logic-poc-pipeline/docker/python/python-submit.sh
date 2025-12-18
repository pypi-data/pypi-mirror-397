#!/bin/bash
# python-submit.sh - Execute Python jobs in container with optional coverage collection

set -e

# Echo Python version
python --version
python -c "import sys; print(sys.path)"

# Log that dependencies are pre-installed
echo "Using pre-installed dependencies from Docker image"

# Enable coverage collection if COVERAGE_ENABLED environment variable is set
if [ "${COVERAGE_ENABLED}" = "true" ]; then
    echo "🔍 Coverage collection enabled for containerized execution"
    
    # Install coverage if not present
    python -c "import coverage" 2>/dev/null || pip install coverage
    
    # Set coverage configuration
    export COVERAGE_FILE="/app/data/.coverage.container"
    
    # Run with coverage
    echo "Running Python job with coverage instrumentation..."
    cd /app
    python -m coverage run --source=/app/src --parallel-mode /app/scripts/container/generic_entry.py "$@"
    
    # Save coverage data to shared volume
    echo "Saving coverage data to shared volume..."
    python -m coverage combine
    cp .coverage* /app/data/ 2>/dev/null || true
    
    echo "✅ Coverage data saved to /app/data/"
else
    # Normal execution without coverage
    cd /app
    python /app/scripts/container/generic_entry.py "$@"
fi