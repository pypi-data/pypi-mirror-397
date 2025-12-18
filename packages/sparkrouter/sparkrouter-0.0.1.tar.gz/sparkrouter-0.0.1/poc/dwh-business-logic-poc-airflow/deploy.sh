#!/bin/bash
# deploy.sh - Build and deploy the business logic code

set -e  # Exit immediately if a command fails

# Environment configuration
ACCOUNT_DEV="dev"
ACCOUNT_SANDBOX="sandbox"
ACCOUNT_PROD="prod"
VALID_ACCOUNTS=("ACCOUNT" "$ACCOUNT_SANDBOX" "$ACCOUNT_DEV" "$ACCOUNT_PROD")

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
ACCOUNT="sandbox"
ENVIRONMENT="jc"
SKIP_VALIDATION=true
SKIP_TESTS=false
SKIP_INTEGRATION=true
SKIP_FUNCTIONAL_TESTS=true
VERSION_OVERRIDE=""

# Function to display usage information
function show_usage {
    echo "Usage: $0 --env=ENVIRONMENT [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  --account=ACCOUNT         Specify deployment account: sandbox, dev, prod"
    echo "  --env=ENVIRONMENT         Specify deployment environment: dev, qa, prod, etc."
    echo ""
    echo "Options:"
    echo "  --no-validate             Skip validation steps during build"
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

# Validate account parameter
if [[ -z "$ACCOUNT" ]]; then
    echo "Error: Account parameter is required."
    show_usage
fi

# Convert environment to lowercase for case-insensitive comparison
ACCOUNT=$(echo "$ACCOUNT" | tr '[:upper:]' '[:lower:]')

# Validate environment parameter
if [[ -z "$ENVIRONMENT" ]]; then
    echo "Error: Environment parameter is required."
    show_usage
fi

# Convert environment to lowercase for case-insensitive comparison
ENVIRONMENT=$(echo "$ENVIRONMENT" | tr '[:upper:]' '[:lower:]')

if [[ "$ACCOUNT" == "$ACCOUNT_SANDBOX" ]]; then
    REGION="us-west-1"
    MWAA_BUCKET="sfly-aws-dwh-sandbox-$ENVIRONMENT-mwaa-$REGION"
    MWAA_PREFIX="mwaa"
elif [[ "$ACCOUNT" == "$ACCOUNT_DEV" ]]; then
    REGION="us-east-1"
    MWAA_BUCKET="sfly-aws-dwh-dev-consumer-mwaa-v1"
    MWAA_PREFIX="mwaa"
elif [[ "$ACCOUNT" == "$ACCOUNT_PROD" ]]; then
    REGION="us-east-1"
    MWAA_BUCKET="sfly-aws-dwh-prod-consumer-mwaa-v1"
    MWAA_PREFIX="mwaa"
else
    echo "Error: Invalid account '$ACCOUNT'. Must be one of: ${VALID_ACCOUNTS[*]}"
    show_usage
fi


echo "Deploying to environment $ENVIRONMENT on account $ACCOUNT"
echo "Region: $REGION"
echo "Bucket: $MWAA_BUCKET"
echo "S3 Prefix: $MWAA_PREFIX"

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

if [ "$SKIP_VALIDATION" = true ]; then
    echo "Skipping code validation (--no-validate set)"
else
    echo "Running code validation..."
    if "$SCRIPT_DIR/code-validation.sh"; then
        echo "✓ Code validation passed"
    else
        echo "✗ Code validation failed"
        exit 1
    fi
fi

# Upload to S3
echo "Uploading artifacts to s3://$MWAA_BUCKET/$MWAA_PREFIX/"
if [[ "$ACCOUNT" == "$ACCOUNT_SANDBOX" ]]; then
    echo "Uploading requirements.txt (sandbox only)"
    aws s3 cp requirements.txt "s3://$MWAA_BUCKET/$MWAA_PREFIX/" --region $REGION
fi

# Operators
aws s3 cp src/operators/__init__.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/operators/"
aws s3 cp src/operators/glue_pyshell_job_creator.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/operators/"

# DAGs
#aws s3 cp src/python_version.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#
#aws s3 cp src/generic_example_glue_pyshell_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#aws s3 cp src/generic_example_glue_pyspark_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#aws s3 cp src/generic_example_databricks_pyspark_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#
#aws s3 cp src/sql_example_glue_pyshell_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#aws s3 cp src/sql_example_glue_pyspark_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#aws s3 cp src/sql_example_databricks_pyspark_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
#aws s3 cp src/load_promos_glue_pyspark_job.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
aws s3 cp src/transform_image_glue_pyspark.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
aws s3 cp src/filter_image_glue_pyspark.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"
aws s3 cp src/event_dispatcher.py "s3://$MWAA_BUCKET/$MWAA_PREFIX/dags/"



if [ $? -eq 0 ]; then
    echo "✓ Successfully uploaded to environment '$ENVIRONMENT' on account '$ACCOUNT': s3://$MWAA_BUCKET/$MWAA_PREFIX"
else
    echo "✗ Failed to upload artifacts to S3"
    exit 1
fi

echo "=== Deployment to $ENVIRONMENT on $ACCOUNT completed successfully! ==="