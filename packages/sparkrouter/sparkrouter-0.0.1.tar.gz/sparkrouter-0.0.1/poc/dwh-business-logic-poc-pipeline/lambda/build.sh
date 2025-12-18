#!/bin/bash
# Build Lambda deployment package

set -e

echo "Building Lambda deployment package..."

# Create temp directory
rm -rf package
mkdir -p package

# Install dependencies
pip install -r requirements.txt -t package/

# Copy Lambda function
cp job_metrics_processor.py package/index.py

# Create zip
cd package
zip -r ../job_metrics_processor.zip .
cd ..

# Clean up
rm -rf package

echo "Lambda package created: job_metrics_processor.zip"
