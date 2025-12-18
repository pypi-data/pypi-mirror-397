#!/bin/bash

# Prevent multiple executions
if [ -n "$ENV_SETUP_DONE" ]; then
    echo "Environment already set up"
    return 0 2>/dev/null || exit 0
fi

# Get the directory of this script and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="${SCRIPT_DIR}"

# Source the global environment setup
source "${PROJECT_ROOT}/setup-global-env.sh"

# If global setup failed, exit
if [ $? -ne 0 ]; then
    echo "Global environment setup failed"
    return 1 2>/dev/null || exit 1
fi

#echo "Using Python: $PYTHON_CMD"

# Set up virtual environment if it doesn't exist
VENV_DIR="${SCRIPT_DIR}/.venv"
if [ ! -d "${VENV_DIR}" ]; then
    echo "Creating virtual environment..."
    ${PYTHON_CMD} -m venv "${VENV_DIR}" || {
        echo "Failed to create virtual environment with pip."
        exit 1
    }

    # Check if venv was created successfully
    if [ ! -f "${VENV_DIR}/bin/activate" ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# After venv creation
if [ ! -x "${VENV_DIR}/bin/python" ]; then
    echo "Virtual environment creation failed. Exiting."
    return 1 2>/dev/null || exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "${VENV_DIR}/bin/activate" || {
    echo "Failed to activate virtual environment. Using system Python."
#    export PATH="/usr/bin:$PATH"
    exit 1
}

# Update PYTHON_CMD to use the virtual environment's Python explicitly
PYTHON_CMD="${VENV_DIR}/bin/python"
export PYTHON_CMD

echo "Project Environment Python: $PYTHON_CMD"

# Check if pip is available in the virtual environment
if ! "${PYTHON_CMD}" -c "import pip" &>/dev/null; then
    echo "pip not available in virtual environment. Installing pip..."
    exit 1
fi

# Now try to upgrade pip inside the virtual environment
#if "${PYTHON_CMD}" -c "import pip" &>/dev/null; then
#    echo "Upgrading pip within virtual environment..."
#    "${PYTHON_CMD}" -m pip install --upgrade pip wheel setuptools
#else
#    echo "Warning: pip still not available. Some functionality may be limited."
#fi

## Install requirements
if [ -f "${SCRIPT_DIR}/requirements-dev.txt" ]; then
    if "${PYTHON_CMD}" -c "import pip" &>/dev/null; then
      echo "Installing development requirements..."
        cd "${SCRIPT_DIR}" # Change to script directory before running pip
        "${PYTHON_CMD}" -m pip install --use-pep517 -r "${SCRIPT_DIR}/requirements-dev.txt" || {
          echo "Failed to install all requirements."
          exit 1
        }
    else
        echo "Warning: Cannot install requirements because pip is not available."
        exit 1
    fi
fi

## Ensure essential packages are installed
#for pkg in pytest flake8; do
#    if ! "${PYTHON_CMD}" -c "import $pkg" &>/dev/null; then
#        echo "Installing $pkg..."
#        if "${PYTHON_CMD}" -c "import pip" &>/dev/null; then
#            "${PYTHON_CMD}" -m pip install --use-pep517 $pkg
#        else
#            echo "Warning: Cannot install $pkg because pip is not available."
#        fi
#    fi
#done

# Mark environment setup as complete
export ENV_SETUP_DONE=1

echo "Environment setup complete"
