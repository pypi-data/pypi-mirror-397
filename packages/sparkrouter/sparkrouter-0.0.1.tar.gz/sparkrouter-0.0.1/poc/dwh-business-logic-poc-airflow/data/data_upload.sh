#!/bin/bash

SOURCE_DIR="./data"
DESTINATION="s3://sfly-aws-dwh-sandbox-poc-data/input/"
REGION="us-east-1"

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "Error: Source directory '$SOURCE_DIR' not found."
    exit 1
fi

# Count files to upload (excluding .sh files)
FILE_COUNT=$(find "$SOURCE_DIR" -type f -not -name "*.sh" | wc -l)
if [ "$FILE_COUNT" -eq 0 ]; then
    echo "Warning: No files (excluding .sh files) found in '$SOURCE_DIR'. Nothing to upload."
    exit 0
fi

echo "Found $FILE_COUNT non-script files in $SOURCE_DIR to upload to $DESTINATION"
echo "Uploading files to S3 bucket..."

# Upload files to S3 (exclude .sh files)
if aws s3 sync "$SOURCE_DIR" "$DESTINATION" --region "$REGION" \
   --exclude "*.sh"; then
    echo "Upload complete!"
    echo "Files are now available in S3."
else
    echo "Error: Failed to upload files to S3."
    exit 1
fi