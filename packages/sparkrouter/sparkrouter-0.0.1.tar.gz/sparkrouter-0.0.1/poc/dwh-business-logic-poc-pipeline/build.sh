#!/bin/bash
# build.sh - Build the Python wheel package
set -e  # Exit immediately if a command fails

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Parse command line arguments
SKIP_VALIDATION=false
SKIP_TESTS=false
SKIP_FUNCTIONAL_TESTS=false
SKIP_INTEGRATION_TESTS=false
VERSION_OVERRIDE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-validate)
            SKIP_VALIDATION=true
            shift
            ;;
        --no-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-functional-tests)
            SKIP_FUNCTIONAL_TESTS=true
            shift
            ;;
        --no-integration-tests)
            SKIP_INTEGRATION_TESTS=true
            shift
            ;;
        --version=*)
            VERSION_OVERRIDE="${1#*=}"
            shift
            ;;
        --version)
            VERSION_OVERRIDE="$2"
            shift 2
            ;;
        *)
            shift
            ;;
    esac
done

# Debug: Show skip flags
# echo "DEBUG: SKIP_TESTS=$SKIP_TESTS, SKIP_FUNCTIONAL_TESTS=$SKIP_FUNCTIONAL_TESTS"

# Source the environment setup script
if [ -f "$SCRIPT_DIR/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "$SCRIPT_DIR/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

# Run code validation if not skipped
if [ "$SKIP_VALIDATION" = false ]; then
    echo "Validating code..."

    VALIDATION_ARGS=""
    if [ "$SKIP_TESTS" = true ]; then
        VALIDATION_ARGS="$VALIDATION_ARGS --no-tests"
    fi
    if [ "$SKIP_FUNCTIONAL_TESTS" = true ]; then
        VALIDATION_ARGS="$VALIDATION_ARGS --no-functional-tests"
    fi
    if [ "$SKIP_INTEGRATION_TESTS" = true ]; then
        VALIDATION_ARGS="$VALIDATION_ARGS --no-integration-tests"
    fi
    if "$SCRIPT_DIR/code-validation.sh" $VALIDATION_ARGS; then
        echo "✓ Code validation passed"
    else
        echo "✗ Code validation failed"
        echo "Fix the issues before building or run with --no-validate to skip validation"
        exit 1
    fi
    # Skip all tests if SKIP_TESTS is true
    if [ "$SKIP_TESTS" = true ]; then
        echo "Skipping unit tests"
        echo "Skipping functional tests"
    else
        echo "Running unit tests..."
        if "$SCRIPT_DIR/unit-tests.sh"; then
            echo "✓ Unit tests passed"
        else
            echo "✗ Unit tests failed"
            echo "Fix the issues before building or run with --no-tests to skip tests"
            exit 1
        fi
        if [ "$SKIP_FUNCTIONAL_TESTS" = false ]; then
            echo "Running functional tests..."
            if "$SCRIPT_DIR/functional-tests.sh"; then
                echo "✓ Functional tests passed"
            else
                echo "✗ Functional tests failed"
                echo "Fix the issues before building or run with --no-functional-tests to skip functional tests"
                exit 1
            fi
        else
            echo "Skipping functional tests"
        fi
        if [ "$SKIP_INTEGRATION_TESTS" = false ]; then
            echo "Running integration tests..."
            if "$SCRIPT_DIR/integration-tests.sh"; then
                echo "✓ Integration tests passed"
            else
                echo "✗ Integration tests failed"
                echo "Fix the issues before building or run with --no-integration-tests to skip integration tests"
                exit 1
            fi
        else
            echo "Skipping integration tests"
        fi
    fi
else
    # If validation is skipped but tests are not, run tests unless SKIP_TESTS is true
    if [ "$SKIP_TESTS" = true ]; then
        echo "Skipping code validation, unit tests, and functional tests"
    else
        echo "Running unit tests..."
        if "$SCRIPT_DIR/unit-tests.sh"; then
            echo "✓ Unit tests passed"
        else
            echo "✗ Unit tests failed"
            echo "Fix the issues before building or run with --no-tests to skip tests"
            exit 1
        fi
        if [ "$SKIP_FUNCTIONAL_TESTS" = false ]; then
            echo "Running functional tests..."
            if "$SCRIPT_DIR/functional-tests.sh"; then
                echo "✓ Functional tests passed"
            else
                echo "✗ Functional tests failed"
                echo "Fix the issues before building or run with --no-functional-tests to skip functional tests"
                exit 1
            fi
        else
            echo "Skipping functional tests"
        fi
        if [ "$SKIP_INTEGRATION_TESTS" = false ]; then
            echo "Running integration tests..."
            if "$SCRIPT_DIR/integration-tests.sh"; then
                echo "✓ Integration tests passed"
            else
                echo "✗ Integration tests failed"
                echo "Fix the issues before building or run with --no-integration-tests to skip integration tests"
                exit 1
            fi
        else
            echo "Skipping integration tests"
        fi
    fi
fi

# Install build requirements
echo "Installing build requirements..."
# Use --no-user flag to force installation to the virtual environment instead of user site
"$PYTHON_CMD" -m pip install --no-user --use-pep517 wheel build --quiet

# Verify build package was installed correctly
if ! "$PYTHON_CMD" -c "import build" &>/dev/null; then
    echo "ERROR: Failed to install 'build' package. Trying alternative approach..."
    # Try installing with more verbose output to diagnose issues
    "$PYTHON_CMD" -m pip install --no-user --verbose build
    
    # Check again if build is available
    if ! "$PYTHON_CMD" -c "import build" &>/dev/null; then
        echo "ERROR: Critical failure - could not install 'build' package. Cannot continue."
        exit 1
    fi
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Get code version from VERSION file or override
if [ -z "$VERSION_OVERRIDE" ]; then
    CODE_VERSION=$(cat VERSION)
    echo "Building version from VERSION file: $CODE_VERSION"
else
    CODE_VERSION="$VERSION_OVERRIDE"
    echo "Building with overridden version: $CODE_VERSION"
fi

# Build the wheel
echo "Building wheel package..."
"$PYTHON_CMD" -m build --wheel

# Find the wheel file
WHEEL_FILE=$(find dist -name "*.whl" | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "Error: No wheel file was built"
    exit 1
fi

echo "✓ Successfully built: $WHEEL_FILE"