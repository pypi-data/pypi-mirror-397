#!/bin/bash
# setup-global-env.sh - Global environment setup for all projects

# Prevent multiple executions
if [ -n "$GLOBAL_ENV_SETUP_DONE" ]; then
    echo "Global environment already set up"
    return 0 2>/dev/null || exit 0
fi

# Find the Python interpreter to use
if command -v python &>/dev/null; then
    PYTHON_CMD=$(which python)
elif command -v python3 &>/dev/null; then
    PYTHON_CMD=$(which python3)
else
    echo "Error: Python not found. Install with: sudo apt install python3 python3-pip python3-venv"
    return 1 2>/dev/null || exit 1
fi

echo "Project Python: $PYTHON_CMD"

# Export the Python command for other scripts to use
export PYTHON_CMD

# Check if venv module is available
if ! ${PYTHON_CMD} -c "import venv" &>/dev/null; then
    echo "Python venv module not available. Installing python3-venv..."
    echo "Run: sudo apt install python3-venv"
    return 1 2>/dev/null || exit 1
fi

# Remove the global pip upgrade that causes warnings
# This will be done in the virtual environment instead

# Mark global setup as complete
export GLOBAL_ENV_SETUP_DONE=1

echo "Global environment setup complete"