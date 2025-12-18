# Business Logic Shell Scripts

This document describes the shell scripts used for building, testing, and deploying the business logic code.

## Environment Setup Scripts

### setup-global-env.sh (Project Root)
- **Purpose**: Sets up global environment variables and checks for Python availability
- **Location**: Project root directory
- **Called by**: All project-specific setup-env.sh scripts
- **Runs only once**: Uses `GLOBAL_ENV_SETUP_DONE` flag to prevent multiple executions

### setup-env.sh (Project Level)
- **Purpose**: Sets up project-specific environment, including virtual environment and dependencies
- **Location**: Business logic and MWAA directories
- **Called by**: All other scripts
- **Runs only once**: Uses `ENV_SETUP_DONE` flag to prevent multiple executions
- **Dependencies**: Calls setup-global-env.sh

## Build and Test Scripts

### unit-tests.sh
- **Purpose**: Runs unit tests (non-integration tests)
- **Usage**: `./unit-tests.sh [test_directory]`
- **Dependencies**: setup-env.sh

### code-validation.sh
- **Purpose**: Validates code using flake8
- **Usage**: `./code-validation.sh [source_directory] [flake8_config]`
- **Dependencies**: unit-tests.sh, setup-env.sh

### integration-tests.sh
- **Purpose**: Sets up Docker environment and runs integration tests
- **Usage**: `./integration-tests.sh`
- **Dependencies**: setup-env.sh, Docker, AWS CLI container
- **Note**: Requires Docker to be running

### build.sh
- **Purpose**: Builds Python wheel package
- **Usage**: `./build.sh [--no-validate] [--no-tests] [--version=X.Y.Z]`
- **Dependencies**: code-validation.sh, unit-tests.sh, setup-env.sh
- **Flags**:
  - `--no-validate`: Skip code validation
  - `--no-tests`: Skip unit tests
  - `--version=X.Y.Z`: Override version number (instead of using VERSION file)

### deploy.sh
- **Purpose**: Builds and deploys code to S3
- **Usage**: `./deploy.sh [--no-validate] [--no-tests] [--no-integration] [--version=X.Y.Z]`
- **Dependencies**: build.sh, integration-tests.sh, AWS CLI
- **Flags**:
  - `--no-validate`: Skip code validation
  - `--no-tests`: Skip unit tests
  - `--no-integration`: Skip integration tests
  - `--version=X.Y.Z`: Override version number (instead of using VERSION file)

## Execution Order

The typical execution order is:

1. **setup-global-env.sh** - Called by setup-env.sh
2. **setup-env.sh** - Called by all other scripts
3. **unit-tests.sh** - Run unit tests
4. **code-validation.sh** - Validates code (calls unit-tests.sh)
5. **build.sh** - Builds package (calls code-validation.sh)
6. **integration-tests.sh** - Runs integration tests
7. **deploy.sh** - Deploys code (calls build.sh and integration-tests.sh)

## Requirements

- Bash shell environment
- Python 3.x with venv module
- Docker (for integration tests)
- AWS CLI (for deployment)

## Examples

### Full Build and Deploy
```bash
./deploy.sh
```

### Build Only (No Tests)
```bash
./build.sh --no-validate --no-tests
```

### Deploy Without Integration Tests
```bash
./deploy.sh --no-integration
```

### Build With Custom Version
```bash
./build.sh --version=1.2.3
```

### Deploy With Custom Version
```bash
./deploy.sh --version=1.2.3
```

### Run Unit Tests Only
```bash
./unit-tests.sh
```