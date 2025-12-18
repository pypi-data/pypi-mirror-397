#!/bin/bash
# run-coverage.sh - Comprehensive coverage analysis including unit and integration tests

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
cd "${SCRIPT_DIR}"

# Source the environment setup script
if [ -f "${SCRIPT_DIR}/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "${SCRIPT_DIR}/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

echo "=========================================="
echo "    COMPREHENSIVE COVERAGE ANALYSIS"
echo "=========================================="
echo ""

# Clean up previous coverage data
echo "🧹 Cleaning up previous coverage data..."
rm -f .coverage*
rm -rf htmlcov htmlcov_unit htmlcov_integration htmlcov_combined
rm -f unit_coverage.txt integration_coverage.txt combined_coverage.txt

# Run unit tests with coverage
echo ""
echo "🔬 Running unit tests with coverage..."
${PYTHON_CMD} -m coverage run --source=src --parallel-mode -m pytest -x tests/unit/
UNIT_EXIT_CODE=$?

if [ $UNIT_EXIT_CODE -ne 0 ]; then
    echo "❌ Unit tests failed. Exiting..."
    exit $UNIT_EXIT_CODE
fi

# Generate unit-only coverage report
echo ""
echo "📊 Generating unit test coverage report..."
${PYTHON_CMD} -m coverage combine
${PYTHON_CMD} -m coverage report --show-missing > unit_coverage.txt
${PYTHON_CMD} -m coverage html -d htmlcov_unit
echo "Unit coverage report saved to:"
echo "  - Text: unit_coverage.txt"
echo "  - HTML: htmlcov_unit/"

# Save unit coverage data
cp .coverage .coverage.unit

# Run integration tests with coverage
echo ""
echo "🔗 Running integration tests with coverage..."
./integration-tests.sh
INTEGRATION_EXIT_CODE=$?

# Combine all coverage data
echo ""
echo "🔀 Combining unit and integration coverage..."

# Combine all coverage files
${PYTHON_CMD} -m coverage combine .coverage.unit .coverage

# Generate combined coverage report
echo ""
echo "📈 Generating combined coverage report..."
${PYTHON_CMD} -m coverage report --show-missing > combined_coverage.txt
${PYTHON_CMD} -m coverage html -d htmlcov_combined

echo ""
echo "=========================================="
echo "           COVERAGE SUMMARY"
echo "=========================================="
echo ""

# Display coverage summaries
if [ -f unit_coverage.txt ]; then
    echo "📊 UNIT TEST COVERAGE:"
    tail -n 3 unit_coverage.txt
    echo ""
fi

if [ -f integration_coverage.txt ]; then
    echo "🔗 INTEGRATION TEST COVERAGE:"
    tail -n 3 integration_coverage.txt
    echo ""
fi

echo "🎯 COMBINED COVERAGE:"
tail -n 3 combined_coverage.txt

echo ""
echo "=========================================="
echo "         COVERAGE ANALYSIS"
echo "=========================================="
echo ""

# Extract coverage percentage for analysis
COMBINED_COVERAGE=$(tail -n 1 combined_coverage.txt | grep -o '[0-9]*%' | head -n 1 | tr -d '%')

if [ -n "$COMBINED_COVERAGE" ]; then
    echo "📈 Combined Coverage: ${COMBINED_COVERAGE}%"
    
    if [ "$COMBINED_COVERAGE" -ge 80 ]; then
        echo "✅ Coverage target (80%) achieved!"
    else
        NEEDED=$((80 - COMBINED_COVERAGE))
        echo "⚠️  Need ${NEEDED}% more coverage to reach 80% target"
        
        echo ""
        echo "🎯 TOP AREAS FOR IMPROVEMENT:"
        echo "   Check htmlcov_combined/index.html for detailed analysis"
        
        # Show files with lowest coverage
        echo ""
        echo "📉 Files with lowest coverage:"
        grep -E "^src/" combined_coverage.txt | sort -k4 -n | head -5
    fi
fi

echo ""
echo "📁 Coverage Reports Available:"
echo "  - Combined HTML: htmlcov_combined/index.html"
echo "  - Unit HTML: htmlcov_unit/index.html"
echo "  - Integration HTML: htmlcov_integration/index.html"
echo "  - Combined Text: combined_coverage.txt"

# Exit with the integration test exit code
exit $INTEGRATION_EXIT_CODE