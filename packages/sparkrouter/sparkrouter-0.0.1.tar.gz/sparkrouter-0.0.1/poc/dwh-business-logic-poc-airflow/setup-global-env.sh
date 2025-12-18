#!/bin/bash
# setup-global-env.sh - Global environment setup for all projects

# Prevent multiple executions
if [ -n "$GLOBAL_ENV_SETUP_DONE" ]; then
    echo "Global environment already set up"
    return 0 2>/dev/null || exit 0
fi

# Prefer python3.11 if available
if command -v python3.11 &>/dev/null; then
    PYTHON_CMD=$(which python3.11)
else
    echo "Python 3.11 not found."
    echo "Please install it with:"
    echo "  sudo add-apt-repository ppa:deadsnakes/ppa"
    echo "  sudo apt-get update"
    echo "  sudo apt-get install python3.11 python3.11-venv python3.11-dev"
    return 1 2>/dev/null || exit 1
fi

echo "Project Python: $PYTHON_CMD"
export PYTHON_CMD

if ! ${PYTHON_CMD} -c "import venv" &>/dev/null; then
    echo "Python venv module not available. Install with:"
    echo "  sudo apt-get install python3.11-venv"
    return 1 2>/dev/null || exit 1
fi

export GLOBAL_ENV_SETUP_DONE=1
echo "Global environment setup complete"