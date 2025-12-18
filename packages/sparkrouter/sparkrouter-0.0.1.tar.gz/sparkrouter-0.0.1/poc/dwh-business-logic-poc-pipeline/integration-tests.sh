#!/bin/bash
# integration-tests.sh - Run integration tests for the business logic code

# Set the default AWS region for LocalStack
export AWS_DEFAULT_REGION=us-east-1

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Change to business-logic directory for docker-compose
cd "${SCRIPT_DIR}"

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "ERROR: AWS CLI is not installed or not in PATH"
    echo "Please install AWS CLI using one of the following methods:"
    echo "  - Windows: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    echo "  - macOS: brew install awscli"
    echo "  - Linux: sudo apt-get install awscli"
    echo "After installation, configure AWS CLI with: aws configure"
    exit 1
fi

# Source the environment setup script
if [ -f "${SCRIPT_DIR}/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "${SCRIPT_DIR}/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

# Use PYTHON_CMD from setup-env.sh instead of $(which python)
CURRENT_PYTHON="$PYTHON_CMD"
echo "Integration Tests Using Python: $CURRENT_PYTHON"

# We don't need to check for JAVA_HOME anymore since we're using Docker Spark
# Instead, make sure Docker is running
if ! docker ps &>/dev/null; then
    echo "ERROR: Docker is not running. Please start Docker first."
    exit 1
fi

# Flag to track if we started docker-compose
STARTED_DOCKER=0

# Check if localstack and spark containers are running
if ! (docker ps | grep -q localstack) || ! (docker ps | grep -q "spark.*master"); then
    echo "Starting docker-compose services..."
    # Remove LocalStack volumes before starting
    docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" down -v
    docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" up -d
    STARTED_DOCKER=1

    # Give LocalStack some initial time to start
    echo "Giving LocalStack initial startup time..."
    sleep 10
else
    echo "Docker-compose services are already running"
fi

# Function to check if the bucket exists
check_bucket_exists() {
    aws --endpoint-url=http://localhost:4566 --region $AWS_DEFAULT_REGION s3 ls "s3://test-s3-bucket" > /dev/null 2>&1
}

# Function to create the bucket if it doesn't exist
create_test_bucket() {
    if check_bucket_exists; then
        echo "Bucket 'test-s3-bucket' already exists."
        return 0
    else
        echo "Creating test bucket..."
        if aws --endpoint-url=http://localhost:4566 --region $AWS_DEFAULT_REGION s3 mb s3://test-s3-bucket; then
            echo "Bucket 'test-s3-bucket' created successfully."
            return 0
        else
            echo "ERROR: Failed to create test bucket"
            return 1
        fi
    fi
}

# Wait for LocalStack to be ready
echo "Waiting for LocalStack to be ready..."
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:4566/_localstack/health > /dev/null 2>&1; then
        echo "LocalStack service is responding to health check"
        if create_test_bucket; then
            echo "S3 functionality verified - LocalStack is ready!"
            break
        fi
    fi
    attempt=$((attempt+1))
    echo "Waiting for LocalStack... ($attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "LocalStack service did not become ready in time"
    echo "Showing docker logs for troubleshooting:"
    docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" logs localstack
    if [ $STARTED_DOCKER -eq 1 ]; then
        docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" down -v
    fi
    exit 1
fi

# Wait for Spark to be ready
echo "Waiting for Spark to be ready..."
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8080 > /dev/null 2>&1; then
        echo "Spark master is responding - Spark is ready!"
        break
    fi
    attempt=$((attempt+1))
    echo "Waiting for Spark... ($attempt/$max_attempts)"
    sleep 5
done

if [ $attempt -eq $max_attempts ]; then
    echo "Spark service did not become ready in time"
    echo "Showing docker logs for troubleshooting:"
    docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" logs databricks
    if [ $STARTED_DOCKER -eq 1 ]; then
        docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" down -v
    fi
    exit 1
fi

# Run the integration tests
echo "Running integration tests..."
cd "${SCRIPT_DIR}"

# Run the tests with coverage and capture the exit code
echo "Running integration tests with coverage collection..."
#${PYTHON_CMD} -m coverage run --source=src --parallel-mode -m pytest -xs -vvv -m integration
$CURRENT_PYTHON -m pytest -xs -vvv -m integration
TEST_EXIT_CODE=$?

# Combine coverage data if it exists
#if [ -f .coverage* ]; then
#    echo "Combining coverage data..."
#    ${PYTHON_CMD} -m coverage combine
#
#    # Generate integration coverage report
#    echo "Generating integration coverage report..."
#    ${PYTHON_CMD} -m coverage report --show-missing > integration_coverage.txt
#    ${PYTHON_CMD} -m coverage html -d htmlcov_integration
#
#    echo "Integration coverage report saved to:"
#    echo "  - Text: integration_coverage.txt"
#    echo "  - HTML: htmlcov_integration/"
#fi

# Clean up if we started docker-compose
if [ $STARTED_DOCKER -eq 1 ]; then
    echo "Stopping docker-compose services that we started..."
    docker-compose -f "${SCRIPT_DIR}/docker/docker-compose.yml" down -v
else
    echo "Leaving existing docker-compose services running"
fi

# Exit with the test exit code
exit $TEST_EXIT_CODE