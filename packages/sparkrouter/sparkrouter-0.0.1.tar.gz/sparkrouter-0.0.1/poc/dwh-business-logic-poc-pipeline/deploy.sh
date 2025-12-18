#!/bin/bash
# deploy.sh - Build and deploy the business logic code

set -e  # Exit immediately if a command fails

# Environment configuration
ACCOUNT_SANDBOX="sandbox"
ACCOUNT_DEV="dev"
ACCOUNT_PROD="prod"
VALID_ACCOUNTS=("$ACCOUNT_SANDBOX" "$ACCOUNT_DEV" "$ACCOUNT_PROD")

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
ACCOUNT="sandbox"
ENVIRONMENT="jc"
SKIP_VALIDATION=true
SKIP_TESTS=true
SKIP_INTEGRATION=true
SKIP_FUNCTIONAL_TESTS=false
VERSION_OVERRIDE=""

# Function to display usage information
function show_usage {
    echo "Usage: $0 --account=ACCOUNT --env=ENVIRONMENT [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --account=ACCOUNT        Specify deployment account: sandbox, dev, prod"
    echo "  --env=ENVIRONMENT         Specify deployment environment: dev, qa, prod"
    echo ""
    echo "Options:"
    echo "  --no-validate             Skip validation steps during build"
    echo "  --no-tests                Skip running tests during build"
    echo "  --no-functional-tests     Skip running functional tests during build"
    echo "  --no-integration          Skip running integration tests"
    echo "  --version=VERSION         Override version number"
    echo ""
    exit 1
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --account=*)
            ACCOUNT="${1#*=}"
            shift
            ;;
        --account)
            ACCOUNT="$2"
            shift 2
            ;;
        --env=*)
            ENVIRONMENT="${1#*=}"
            shift
            ;;
        --env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        --no-validate)
            SKIP_VALIDATION=true
            shift
            ;;
        --no-tests)
            SKIP_TESTS=true
            shift
            ;;
        --no-integration)
            SKIP_INTEGRATION=true
            shift
            ;;
        --no-functional-tests)
            SKIP_FUNCTIONAL_TESTS=true
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
        --help)
            show_usage
            ;;
        *)
            shift
            ;;
    esac
done

# Validate environment parameter
if [[ -z "$ACCOUNT" ]]; then
    echo "Error: Account parameter is required."
    show_usage
fi

# Convert environment to lowercase for case-insensitive comparison
ACCOUNT=$(echo "$ACCOUNT" | tr '[:upper:]' '[:lower:]')

# Check if environment is valid
if [[ ! " ${VALID_ACCOUNTS[*]} " =~ " ${ACCOUNT} " ]]; then
    echo "Error: Invalid account '$ACCOUNT'. Must be one of: ${VALID_ACCOUNTS[*]}"
    show_usage
fi

# Validate environment parameter
if [[ -z "$ENVIRONMENT" ]]; then
    echo "Error: Environment parameter is required."
    show_usage
fi

# Convert environment to lowercase for case-insensitive comparison
ENVIRONMENT=$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')

# Set environment-specific parameters
if [[ "$ACCOUNT" == "$ACCOUNT_SANDBOX" ]]; then
    # Validate user initials for sandbox
    REGION="us-west-1"
    CODE_BUCKET="sfly-aws-dwh-sandbox-$ENVIRONMENT-code-$REGION"
    S3_PREFIX="code"
elif [[ "$ACCOUNT" == "$ACCOUNT_DEV" ]]; then
    REGION="us-east-1"
    CODE_BUCKET="sfly-aws-dwh-dev-consumer-databricks-scripts"
    S3_PREFIX="code"
#elif [[ "$ENVIRONMENT" == "$ENV_QA" ]]; then
#    REGION="us-east-1"
#    CODE_BUCKET="sfly-aws-dwh-qa-consumer-databricks-scripts" # Assuming naming convention
#    S3_PREFIX="code"
elif [[ "$ACCOUNT" == "$ENV_PROD" ]]; then
    if [[ "$ENVIRONMENT" == "qa" ]]; then
        REGION="us-east-1"
        CODE_BUCKET="sfly-aws-dwh-qa-consumer-databricks-scripts" # Assuming naming convention
        S3_PREFIX="code"
    elif [[ "$ENVIRONMENT" == "prod" ]]; then
        REGION="us-east-1"
        CODE_BUCKET="sfly-aws-dwh-prod-consumer-databricks-scripts"
        S3_PREFIX="code"
    else
        echo "Error: Invalid environment '$ENVIRONMENT' for account '$ACCOUNT'. Must be one of: qa, prod"
        show_usage
    fi
else
    echo "Error: Invalid account '$ACCOUNT'. Must be one of: ${VALID_ACCOUNTS[*]}"
    show_usage
fi

echo "Deploying to environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "Bucket: $CODE_BUCKET"
echo "S3 Prefix: $S3_PREFIX"

# Change to the script directory
cd "$SCRIPT_DIR"

# Source the environment setup script
if [ -f "$SCRIPT_DIR/setup-env.sh" ]; then
    echo "Sourcing environment setup script..."
    source "$SCRIPT_DIR/setup-env.sh"
else
    echo "Error: setup-env.sh not found. Cannot proceed."
    exit 1
fi

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

# Build the package
BUILD_ARGS=""
if [ "$SKIP_VALIDATION" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-validate"
fi
if [ "$SKIP_TESTS" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-tests"
fi
if [ "$SKIP_FUNCTIONAL_TESTS" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-functional-tests"
fi
if [ -n "$VERSION_OVERRIDE" ]; then
    BUILD_ARGS="$BUILD_ARGS --version=$VERSION_OVERRIDE"
fi

# Debug: Show build args
echo "DEBUG: BUILD_ARGS='$BUILD_ARGS'"

echo "Building package..."
# Use eval to ensure arguments are split correctly
eval "\"$SCRIPT_DIR/build.sh\" $BUILD_ARGS"
BUILD_EXIT_CODE=$?
if [ $BUILD_EXIT_CODE -eq 0 ]; then
    echo "✓ Build successful"
else
    echo "✗ Build failed"
    exit 1
fi

# Run integration tests if not skipped
if [ "$SKIP_INTEGRATION" = false ]; then
    echo "Running integration tests..."
    if "$SCRIPT_DIR/integration-tests.sh"; then
        echo "✓ Integration tests passed"
    else
        echo "✗ Integration tests failed"
        echo "Fix the issues before deploying or run with --no-integration to skip integration tests"
        exit 1
    fi
else
    echo "Skipping integration tests"
fi

# Get code version from VERSION file or override
if [ -z "$VERSION_OVERRIDE" ]; then
    CODE_VERSION=$(cat VERSION)
    echo "Deploying version from VERSION file: $CODE_VERSION"
else
    CODE_VERSION="$VERSION_OVERRIDE"
    echo "Deploying with overridden version: $CODE_VERSION"
fi

CODE_PREFIX="$S3_PREFIX/$CODE_VERSION"

# Find the wheel file
WHEEL_FILE=$(find dist -name "*.whl" | head -1)
if [ -z "$WHEEL_FILE" ]; then
    echo "Error: No wheel file was built"
    exit 1
fi

# Upload to S3
echo "Uploading artifacts to s3://$CODE_BUCKET/$CODE_PREFIX/"

# Check if we can use AWS CLI from Docker container
#if docker ps | grep -q "docker-awscli-1"; then
#    echo "Using AWS CLI from Docker container..."
#    AWS_CMD="docker exec docker-awscli-1 aws"
#else
#    echo "Using local AWS CLI..."
#    AWS_CMD="aws"
#fi

aws s3 cp jars/decryption-udfs_2.12-1.0.0.jar "s3://$CODE_BUCKET/$CODE_PREFIX/jars/decryption-udfs_2.12-1.0.0.jar" --region $REGION
aws s3 cp jars/platform.infrastructure-1.19.5-SNAPSHOT.jar "s3://$CODE_BUCKET/$CODE_PREFIX/jars/platform.infrastructure-1.19.5-SNAPSHOT.jar" --region $REGION

aws s3 cp "$WHEEL_FILE" "s3://$CODE_BUCKET/$CODE_PREFIX/" --region $REGION
aws s3 cp requirements.txt "s3://$CODE_BUCKET/$CODE_PREFIX/" --region $REGION
aws s3 sync scripts "s3://$CODE_BUCKET/$CODE_PREFIX/scripts" --region $REGION --delete
aws s3 sync schemas "s3://$CODE_BUCKET/$CODE_PREFIX/schemas" --region $REGION --delete

# Upload orchestration configs
if [ -d "orchestration" ]; then
    echo "Uploading orchestration configs..."
    aws s3 sync orchestration "s3://$CODE_BUCKET/$CODE_PREFIX/orchestration" --region $REGION --delete
    echo "✓ Orchestration configs uploaded to s3://$CODE_BUCKET/$CODE_PREFIX/orchestration/"
fi

if [ $? -eq 0 ]; then
    echo "✓ Successfully uploaded to environment '$ENVIRONMENT' on account '$ACCOUNT': s3://$CODE_BUCKET/$CODE_PREFIX/$(basename $WHEEL_FILE)"
else
    echo "✗ Failed to upload wheel to S3"
    exit 1
fi

echo "=== Deployment to $ENVIRONMENT on '$ACCOUNT' completed successfully! ==="