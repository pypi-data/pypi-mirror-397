#!/bin/bash
# code-validation.sh - Validate code using flake8

set -e  # Exit on any error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Initialize variables
SKIP_TESTS=false
SKIP_FUNCTIONAL_TESTS=false
SRC_DIR="$SCRIPT_DIR/src"
FLAKE8_CONFIG="$SCRIPT_DIR/.flake8"

# Parse flags first before using any positional arguments
for arg in "$@"; do
    case $arg in
        --no-tests)
            SKIP_TESTS=true
            ;;
        --no-functional-tests)
            SKIP_FUNCTIONAL_TESTS=true
            ;;
        --*) 
            # Skip other flags
            ;;
        *)
            # First non-flag argument is the source directory
            if [ "$SRC_DIR" = "$SCRIPT_DIR/src" ]; then
                SRC_DIR="$arg"
            # Second non-flag argument is the flake8 config
            elif [ "$FLAKE8_CONFIG" = "$SCRIPT_DIR/.flake8" ]; then
                FLAKE8_CONFIG="$arg"
            fi
            ;;
    esac
done

echo "=== Starting Code Validation ==="
echo "Source Directory: $SRC_DIR"

# Check if directory exists
if [ ! -d "$SRC_DIR" ]; then
    echo "Error: Directory $SRC_DIR not found"
    exit 1
fi

# Source the environment setup script
if [ -f "$SCRIPT_DIR/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "$SCRIPT_DIR/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

# Run unit tests first
if [ "$SKIP_TESTS" = false ]; then
    echo "Running unit tests as part of validation..."
    if "$SCRIPT_DIR/unit-tests.sh"; then
        echo "✓ Unit tests passed"
    else
        echo "✗ Unit tests failed"
        exit 1
    fi
else
    echo "Skipping unit tests as part of validation"
fi

# Run flake8 for code style validation
echo "Running flake8 linting..."
echo "Code Validation using Python: $PYTHON_CMD"

# Check if flake8 is available
if ! ${PYTHON_CMD} -c "import flake8" &>/dev/null; then
    echo "flake8 not found. Installing..."
    ${PYTHON_CMD} -m pip install flake8
    if [ $? -ne 0 ]; then
        echo "Failed to install flake8. Cannot proceed."
        exit 1
    fi
fi

# Run flake8
if [ -f "$FLAKE8_CONFIG" ]; then
    ${PYTHON_CMD} -m flake8 "$SRC_DIR" --config="$FLAKE8_CONFIG"
else
    ${PYTHON_CMD} -m flake8 "$SRC_DIR"
fi

if [ $? -eq 0 ]; then
    echo "✓ flake8 validation passed"
else
    echo "✗ flake8 validation failed"
    exit 1
fi

echo "=== All code validations passed! ==="
