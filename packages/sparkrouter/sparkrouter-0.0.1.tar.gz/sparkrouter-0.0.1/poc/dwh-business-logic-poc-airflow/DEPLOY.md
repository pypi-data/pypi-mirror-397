# Validation and Deployment Process Documentation

## Overview

This document describes the validation and deployment process implemented in the project. The workflow is split into two independent steps:

1. **Validation**: Code linting and testing
2. **Upload**: Deploying code to S3

These processes can be run independently or together as a complete deployment workflow.

## Components

### `validate.sh`

This script performs code validation through:
- **Linting**: Uses Flake8 to check code style and find potential errors
- **Unit Testing**: Runs pytest to verify code functionality

### `s3_upload.sh`

Handles uploading Python (`.py`) and text (`.txt`) files to an S3 bucket.

### `deploy.sh`

Coordinates the validation and upload processes:
1. First runs validation
2. If validation succeeds, runs upload
3. Reports success or failure

## Running Validation Independently

To validate your code without deployment:

    ./validate.sh

This will:
1. Check if Flake8 is installed
2. Run linting on all Python files in the `src` directory
3. Run unit tests using pytest
4. Exit with code 0 if successful, 1 otherwise

## Running Upload Independently

To upload files without validation:

    ./s3_upload.sh

This will:
1. Upload `.py` and `.txt` files to the configured S3 bucket
2. Exit with code 0 if successful, 1 otherwise

## Running the Complete Deployment

For the full process (validation + upload):

    ./deploy.sh

This will:
1. Run the validation process
2. If validation passes, run the upload process
3. Report on the success or failure of the deployment

## Configuration

### Flake8 Configuration

The project includes a `.flake8` configuration that:
- Sets maximum line length to 120 characters
- Selects specific error types to check for (F,E,W,C,B,D)
- Ignores certain errors (W503, E501, etc.)
- Excludes directories like `.git`, `__pycache__`, etc.
- Sets maximum complexity to 10

### Test Configuration

Tests include verification of:
- General code functionality
- DAG integrity for Airflow workflows

## Prerequisites

- Python
- pip
- Flake8 (optional but recommended)
- pytest
- AWS CLI (configured with appropriate permissions)