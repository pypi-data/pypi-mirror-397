# OpenSearch IAM Role Mapping Setup

## Overview

Lambda needs to authenticate to OpenSearch using IAM. Terraform creates the IAM role and access policy, but the internal OpenSearch role mapping must be configured manually (one-time setup).

## Quick Setup - Run the Script

```bash
cd scripts/
./configure-opensearch-iam.sh
```

This maps the Lambda IAM role to OpenSearch's `all_access` role.

## Manual Setup - Via UI

If the script doesn't work:

1. Get Lambda role ARN: `cd infra/ && terraform output lambda_job_metrics_role_arn`
2. Log into OpenSearch Dashboards (username: `admin`, password: from `infra/local.tf`)
3. Go to: Security → Roles → all_access → Mapped users → Manage mapping
4. Add the Lambda role ARN to **Backend roles**
5. Click Map

## Manual Setup - Via API

```bash
cd infra/

OPENSEARCH_ENDPOINT=$(terraform output -raw opensearch_endpoint)
LAMBDA_ROLE_ARN=$(terraform output -raw lambda_job_metrics_role_arn)
OPENSEARCH_PASSWORD="OpenSearch1234!"  # From local.tf

curl -k -u admin:${OPENSEARCH_PASSWORD} \
  -X PUT "https://${OPENSEARCH_ENDPOINT}/_plugins/_security/api/rolesmapping/all_access" \
  -H 'Content-Type: application/json' \
  -d "{\"backend_roles\": [\"${LAMBDA_ROLE_ARN}\"], \"users\": [\"admin\"]}"
```

## Verify

```bash
curl -k -u admin:${OPENSEARCH_PASSWORD} \
  -X GET "https://${OPENSEARCH_ENDPOINT}/_plugins/_security/api/rolesmapping/all_access"
```

The Lambda role ARN should appear in the `backend_roles` array.

## When to Re-run

- OpenSearch domain is recreated
- Lambda IAM role ARN changes
