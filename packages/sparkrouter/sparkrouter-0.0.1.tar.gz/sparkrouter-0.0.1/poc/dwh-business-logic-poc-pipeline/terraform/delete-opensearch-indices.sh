#!/bin/bash
set -e

cd "$(dirname "$0")"

# Initialize terraform if needed
if ! terraform output -raw opensearch_endpoint &>/dev/null; then
  echo "Running terraform init..."
  terraform init -reconfigure
fi

# Get OpenSearch endpoint
OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint 2>/dev/null || echo "")

if [ -z "$OPENSEARCH_ENDPOINT" ]; then
  echo "ERROR: Could not get opensearch_endpoint from terraform outputs."
  exit 1
fi

# Password - update if different or pass as argument
OPENSEARCH_PASSWORD="${1:-OpenSearch1234!}"

echo "OpenSearch Endpoint: ${OPENSEARCH_ENDPOINT}"
echo ""

# List all indices
echo "Current indices:"
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v" | grep -v "^\." || echo "(none)"

echo ""
echo "Deleting index template..."
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/_index_template/job-events-template" 2>/dev/null || true

echo ""
echo "Deleting all job indices..."

# Delete job-events indices (current naming)
echo "Deleting job-events..."
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/job-events" 2>/dev/null || true

echo "Deleting job-events-*..."
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/job-events-*" 2>/dev/null || true

# Delete job-metrics indices (old naming)
echo "Deleting job-metrics..."
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/job-metrics" 2>/dev/null || true

echo "Deleting job-metrics-*..."
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  -X DELETE "https://${OPENSEARCH_ENDPOINT}/job-metrics-*" 2>/dev/null || true

echo ""
echo ""
echo "Remaining indices:"
curl -k -s -u admin:${OPENSEARCH_PASSWORD} \
  "https://${OPENSEARCH_ENDPOINT}/_cat/indices?v" | grep -v "^\." || echo "(none)"

echo ""
echo "Done. Indices deleted. The next job event will recreate them with correct mappings."
