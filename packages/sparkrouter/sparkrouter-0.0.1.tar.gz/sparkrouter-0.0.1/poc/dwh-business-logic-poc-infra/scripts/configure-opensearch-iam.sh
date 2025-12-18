#!/bin/bash
set -e

cd "$(dirname "$0")/../infra"

# Get values from Terraform
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)
LAMBDA_ROLE_ARN=$(terraform output -raw lambda_job_metrics_role_arn)

# Password from local.tf (update if different)
OPENSEARCH_PASSWORD="OpenSearch1234!"

echo "Configuring OpenSearch IAM role mapping..."
echo "OpenSearch Endpoint: ${OPENSEARCH_ENDPOINT}"
echo "Lambda Role ARN: ${LAMBDA_ROLE_ARN}"
echo ""

# Add Lambda IAM role to all_access role mapping
echo "Adding Lambda IAM role to all_access role mapping..."
RESPONSE=$(curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X PUT "https://${OPENSEARCH_ENDPOINT}/_plugins/_security/api/rolesmapping/all_access" \
  -H 'Content-Type: application/json' \
  -d "{
    \"backend_roles\": [\"${LAMBDA_ROLE_ARN}\"],
    \"users\": [\"admin\"]
  }")

echo "$RESPONSE"

# Check for error in response
if echo "$RESPONSE" | grep -q '"status".*"ERROR\|BAD_REQUEST\|FORBIDDEN'; then
  echo ""
  echo "ERROR: Failed to configure role mapping"
  exit 1
fi

if ! echo "$RESPONSE" | grep -q '"status".*"OK\|CREATED'; then
  echo ""
  echo "ERROR: Unexpected response from OpenSearch"
  exit 1
fi

echo ""
echo "Verifying role mapping..."
VERIFY=$(curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X GET "https://${OPENSEARCH_ENDPOINT}/_plugins/_security/api/rolesmapping/all_access")

echo "$VERIFY" | python -m json.tool

# Check if Lambda role ARN is in the backend_roles
if ! echo "$VERIFY" | grep -q "$LAMBDA_ROLE_ARN"; then
  echo ""
  echo "ERROR: Lambda role ARN not found in role mapping"
  exit 1
fi

echo ""
echo "SUCCESS: Lambda IAM role has been mapped to all_access role."
