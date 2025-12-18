#!/bin/bash
set -e

cd "$(dirname "$0")/../infra"

# Get values from Terraform
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)

# Password from local.tf (update if different)
OPENSEARCH_PASSWORD="OpenSearch1234!"

#INDEX_NAME="${1:-job-metrics}"
INDEX_NAME="${1:-job-metrics-transform-images}"

echo "Deleting OpenSearch index: ${INDEX_NAME}"
echo "OpenSearch Endpoint: ${OPENSEARCH_ENDPOINT}"
echo ""

# Delete the index
curl -k -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/${INDEX_NAME}"

echo ""
echo ""
echo "Index '${INDEX_NAME}' has been deleted."
echo "It will be recreated automatically on the next Lambda invocation."
