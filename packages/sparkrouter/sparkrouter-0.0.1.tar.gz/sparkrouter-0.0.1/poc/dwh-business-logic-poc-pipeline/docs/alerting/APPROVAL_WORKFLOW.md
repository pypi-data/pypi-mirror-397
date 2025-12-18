# Approval Workflow Design

> **⚠️ NOT YET IMPLEMENTED**
>
> This document describes a **proposed future design** for human approval workflows.
> The features described here (email links, API Lambda, CLI tool, dashboard forms)
> have NOT been implemented yet. This document is retained for future reference.
>
> **Current state:** Jobs can publish PENDING_APPROVAL status to the job_events topic,
> and the approval_processor Lambda can process approval decisions, but there is no
> user-facing mechanism to submit approvals yet.

This document describes the human interaction design for approving or rejecting jobs that fail quality checks. It supplements [ALERTING.md](ALERTING.md) and [ALERT_HANDLING.md](ALERT_HANDLING.md).

## Problem Statement

When a job completes with quality status RED:
1. Data has been successfully loaded to the target location
2. Artifacts exist and are complete
3. Quality check failed (e.g., drop rate too high)
4. Human must decide: approve (continue downstream) or reject (fix and rerun)

**The question:** How does a human communicate their decision to the system?

## Interaction Options Considered

| Option | Pros | Cons | Recommended |
|--------|------|------|-------------|
| Email Reply | No new UI, mobile-friendly | Clunky, easy to mistype | No |
| Email with Links | One-click, low friction | Need API + web page | **Yes** |
| Dashboard Action | Full context while deciding | Must log into dashboard | Future |
| Slack Integration | Interactive, where people are | Slack app complexity | Future |
| CLI Tool | Fast for developers, scriptable | Need AWS credentials | **Yes** |

## Recommended Solution

Implement two approval methods:

1. **Email with Links** - Primary method for all users
2. **CLI Tool** - Secondary method for developers

## Email with Links Design

### Alert Email Format

```
From: dwh-alerts@company.com
Subject: [PENDING APPROVAL] transform_images job abc123 - Quality RED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

JOB REQUIRES APPROVAL

Job Name:     transform_images
Job Run ID:   abc123
Timestamp:    2024-01-15 10:30:00 UTC
Status:       PENDING_APPROVAL
Quality:      RED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

FAILED QUALITY CHECKS

  ✗ drop_rate
    Value:     12.0%
    Threshold: 10.0%

PASSED QUALITY CHECKS

  ✓ null_rate
    Value:     2.0%
    Threshold: 5.0%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METRICS SUMMARY

  Records Read:    100,000
  Records Written:  88,000
  Records Dropped:  12,000
  Bytes Written:    1.2 GB
  Duration:         2m 30s

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARTIFACTS

  nautilus:
    Path: s3://dwh-data/nautilus/transformed_images/year=2024/month=01/day=15/
    Records: 50,000

  savedproject:
    Path: s3://dwh-data/savedproject/transformed_images/year=2024/month=01/day=15/
    Records: 38,000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ACTIONS

  [APPROVE] https://dwh-api.company.com/approvals/abc123/approve?token=eyJ...

  [REJECT]  https://dwh-api.company.com/approvals/abc123/reject?token=eyJ...

  [VIEW DASHBOARD] https://dwh-dashboard.company.com/jobs/abc123

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

This link expires in 72 hours.

If you did not expect this email, please ignore it.
```

### Approval Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                      User clicks [APPROVE]                           │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              GET /approvals/{job_run_id}/approve?token=xyz           │
│                                                                      │
│  API Gateway → approval_api Lambda                                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      approval_api Lambda                             │
│                                                                      │
│  1. Decode and validate token                                        │
│     - Check signature (HMAC)                                         │
│     - Check expiration (72 hours default)                            │
│     - Extract job_run_id and action                                  │
│                                                                      │
│  2. Look up job in OpenSearch                                        │
│     - Verify job exists                                              │
│     - Verify status is PENDING_APPROVAL                              │
│     - Get job details for confirmation page                          │
│                                                                      │
│  3. Return confirmation page (HTML)                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     Confirmation Page                                │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │   Approve Job Run                                             │  │
│  │                                                               │  │
│  │   Job: transform_images                                       │  │
│  │   Run ID: abc123                                              │  │
│  │   Quality Status: RED                                         │  │
│  │                                                               │  │
│  │   Failed Check: drop_rate (12% > 10%)                         │  │
│  │                                                               │  │
│  │   Reason for approval: (required)                             │  │
│  │   ┌─────────────────────────────────────────────────────────┐ │  │
│  │   │ Known vendor data issue in batch 2024-01-15.            │ │  │
│  │   │ Acceptable for this run.                                 │ │  │
│  │   └─────────────────────────────────────────────────────────┘ │  │
│  │                                                               │  │
│  │   Your email: jsmith@company.com                              │  │
│  │                                                               │  │
│  │   [ Cancel ]  [ Confirm Approval ]                            │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              POST /approvals/{job_run_id}/confirm                    │
│                                                                      │
│  Body: {                                                             │
│    "token": "xyz...",                                                │
│    "action": "APPROVE",                                              │
│    "reason": "Known vendor data issue...",                           │
│    "decided_by": "jsmith@company.com"                                │
│  }                                                                   │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      approval_api Lambda                             │
│                                                                      │
│  1. Validate token again                                             │
│  2. Validate reason is provided                                      │
│  3. Publish to job_approvals SNS topic:                              │
│     {                                                                │
│       "event_type": "approval_decision",                             │
│       "job_name": "transform_images",                                │
│       "job_run_id": "abc123",                                        │
│       "timestamp": "2024-01-15T11:00:00Z",                           │
│       "decision": "APPROVED",                                        │
│       "decided_by": "jsmith@company.com",                            │
│       "reason": "Known vendor data issue..."                         │
│     }                                                                │
│  4. Return success page                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       Success Page                                   │
│                                                                      │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │   ✓ Job Approved                                              │  │
│  │                                                               │  │
│  │   Job transform_images (abc123) has been approved.            │  │
│  │                                                               │  │
│  │   Downstream processing will resume automatically.            │  │
│  │                                                               │  │
│  │   [ View in Dashboard ]                                       │  │
│  │                                                               │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Token Design

Tokens are signed, time-limited, and single-purpose.

### Token Structure

```
base64url(job_run_id|action|expires|signature)
```

Example decoded:
```
abc123|APPROVE|1705420800|a1b2c3d4e5f6g7h8
```

### Token Generation

```python
import hmac
import hashlib
import time
import base64
import os

# Secret stored in AWS Secrets Manager or SSM Parameter Store
APPROVAL_TOKEN_SECRET = os.environ['APPROVAL_TOKEN_SECRET']
APPROVAL_TOKEN_TTL_HOURS = int(os.environ.get('APPROVAL_TOKEN_TTL_HOURS', 72))


def generate_approval_token(job_run_id: str, action: str) -> str:
    """
    Generate a signed, time-limited approval token.

    Args:
        job_run_id: The job run to approve/reject
        action: APPROVE or REJECT

    Returns:
        URL-safe base64 encoded token
    """
    if action not in ('APPROVE', 'REJECT'):
        raise ValueError(f"Invalid action: {action}")

    expires = int(time.time()) + (APPROVAL_TOKEN_TTL_HOURS * 3600)
    payload = f"{job_run_id}|{action}|{expires}"

    signature = hmac.new(
        APPROVAL_TOKEN_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()[:16]

    token_data = f"{payload}|{signature}"
    token = base64.urlsafe_b64encode(token_data.encode()).decode()

    return token


def validate_approval_token(token: str) -> dict | None:
    """
    Validate token and return payload if valid.

    Args:
        token: The token to validate

    Returns:
        Dict with job_run_id, action, expires if valid, None otherwise
    """
    try:
        decoded = base64.urlsafe_b64decode(token.encode()).decode()
        parts = decoded.split('|')

        if len(parts) != 4:
            return None

        job_run_id, action, expires_str, signature = parts
        expires = int(expires_str)

        # Check expiration
        if expires < time.time():
            return None

        # Verify signature
        payload = f"{job_run_id}|{action}|{expires_str}"
        expected_sig = hmac.new(
            APPROVAL_TOKEN_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()[:16]

        if not hmac.compare_digest(signature, expected_sig):
            return None

        return {
            "job_run_id": job_run_id,
            "action": action,
            "expires": expires
        }

    except Exception:
        return None
```

### Security Considerations

1. **Token is action-specific** - APPROVE token cannot be used to reject
2. **Token expires** - Default 72 hours, configurable
3. **Token is signed** - Cannot be forged without secret
4. **Reason is required** - Audit trail for decisions
5. **Email captured** - Know who approved (from form input or SSO)
6. **Single use** - After approval, job status changes, token becomes invalid

## CLI Tool Design

For developers who prefer command-line:

### Usage

```bash
# Approve a job
$ dwh-approve abc123 --reason "Known vendor issue, acceptable"
Looking up job abc123...
  Job: transform_images
  Status: PENDING_APPROVAL
  Quality: RED (drop_rate: 12%)

Publishing approval...
✓ Approved job abc123
✓ Downstream processing will resume

# Reject a job
$ dwh-reject abc123 --reason "Data too corrupted, need source fix"
Looking up job abc123...
  Job: transform_images
  Status: PENDING_APPROVAL
  Quality: RED (drop_rate: 12%)

Publishing rejection...
✓ Rejected job abc123
✓ Artifacts should be cleaned up and job re-run

# List pending approvals
$ dwh-pending
PENDING APPROVALS (2 jobs)

  abc123  transform_images   2024-01-15 10:30  drop_rate: 12%
  def456  load_customers     2024-01-15 11:45  null_rate: 8%

# Get details
$ dwh-pending abc123
Job Run: abc123
Job Name: transform_images
Timestamp: 2024-01-15 10:30:00 UTC
Status: PENDING_APPROVAL

Quality Checks:
  ✗ drop_rate: 12.0% (threshold: 10.0%)
  ✓ null_rate: 2.0% (threshold: 5.0%)

Metrics:
  Records Read: 100,000
  Records Written: 88,000
  Records Dropped: 12,000

Artifacts:
  nautilus: s3://dwh-data/nautilus/transformed_images/...
  savedproject: s3://dwh-data/savedproject/transformed_images/...

To approve: dwh-approve abc123 --reason "your reason"
To reject:  dwh-reject abc123 --reason "your reason"
```

### Implementation

```python
#!/usr/bin/env python3
"""
CLI tool for approving/rejecting jobs with quality failures.

Requires AWS credentials with permissions to:
- Query OpenSearch (es:ESHttpGet)
- Publish to SNS (sns:Publish)
"""

import argparse
import json
import sys
from datetime import datetime

import boto3


def get_opensearch_client():
    """Create OpenSearch client with AWS auth."""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth

    session = boto3.Session()
    credentials = session.get_credentials()
    region = session.region_name or 'us-west-1'

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )

    # Get endpoint from environment or SSM
    endpoint = get_opensearch_endpoint()

    return OpenSearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def get_opensearch_endpoint():
    """Get OpenSearch endpoint from SSM Parameter Store."""
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name='/dwh/opensearch/endpoint')
    return response['Parameter']['Value']


def get_sns_topic_arn():
    """Get job_approvals SNS topic ARN from SSM Parameter Store."""
    ssm = boto3.client('ssm')
    response = ssm.get_parameter(Name='/dwh/sns/job-approvals-arn')
    return response['Parameter']['Value']


def lookup_job(client, job_run_id: str) -> dict | None:
    """Look up job in OpenSearch."""
    response = client.search(
        index='job-events',
        body={
            'query': {
                'term': {'job_run_id': job_run_id}
            }
        }
    )

    hits = response['hits']['hits']
    if not hits:
        return None

    return hits[0]['_source']


def list_pending_jobs(client) -> list:
    """List all jobs with PENDING_APPROVAL status."""
    response = client.search(
        index='job-events',
        body={
            'query': {
                'term': {'status': 'PENDING_APPROVAL'}
            },
            'sort': [{'timestamp': 'desc'}],
            'size': 100
        }
    )

    return [hit['_source'] for hit in response['hits']['hits']]


def publish_decision(job_run_id: str, job_name: str, decision: str, reason: str, decided_by: str):
    """Publish approval decision to SNS."""
    sns = boto3.client('sns')
    topic_arn = get_sns_topic_arn()

    message = {
        'event_type': 'approval_decision',
        'job_name': job_name,
        'job_run_id': job_run_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'decision': decision,
        'decided_by': decided_by,
        'reason': reason
    }

    sns.publish(
        TopicArn=topic_arn,
        Message=json.dumps(message),
        MessageAttributes={
            'decision': {
                'DataType': 'String',
                'StringValue': decision
            }
        }
    )


def get_current_user() -> str:
    """Get current user identity from AWS STS."""
    sts = boto3.client('sts')
    identity = sts.get_caller_identity()
    # ARN format: arn:aws:iam::123456789:user/jsmith or arn:aws:sts::123456789:assumed-role/...
    arn = identity['Arn']
    return arn.split('/')[-1]


def cmd_approve(args):
    """Handle approve command."""
    client = get_opensearch_client()
    job = lookup_job(client, args.job_run_id)

    if not job:
        print(f"Error: Job {args.job_run_id} not found", file=sys.stderr)
        sys.exit(1)

    if job.get('status') != 'PENDING_APPROVAL':
        print(f"Error: Job {args.job_run_id} is not pending approval (status: {job.get('status')})", file=sys.stderr)
        sys.exit(1)

    print(f"Looking up job {args.job_run_id}...")
    print(f"  Job: {job.get('job_name')}")
    print(f"  Status: {job.get('status')}")
    print(f"  Quality: {job.get('quality_status')}")
    print()

    decided_by = args.user or get_current_user()

    print("Publishing approval...")
    publish_decision(
        job_run_id=args.job_run_id,
        job_name=job.get('job_name'),
        decision='APPROVED',
        reason=args.reason,
        decided_by=decided_by
    )

    print(f"✓ Approved job {args.job_run_id}")
    print("✓ Downstream processing will resume")


def cmd_reject(args):
    """Handle reject command."""
    client = get_opensearch_client()
    job = lookup_job(client, args.job_run_id)

    if not job:
        print(f"Error: Job {args.job_run_id} not found", file=sys.stderr)
        sys.exit(1)

    if job.get('status') != 'PENDING_APPROVAL':
        print(f"Error: Job {args.job_run_id} is not pending approval (status: {job.get('status')})", file=sys.stderr)
        sys.exit(1)

    print(f"Looking up job {args.job_run_id}...")
    print(f"  Job: {job.get('job_name')}")
    print(f"  Status: {job.get('status')}")
    print(f"  Quality: {job.get('quality_status')}")
    print()

    decided_by = args.user or get_current_user()

    print("Publishing rejection...")
    publish_decision(
        job_run_id=args.job_run_id,
        job_name=job.get('job_name'),
        decision='REJECTED',
        reason=args.reason,
        decided_by=decided_by
    )

    print(f"✓ Rejected job {args.job_run_id}")
    print("✓ Artifacts should be cleaned up and job re-run")


def cmd_pending(args):
    """Handle pending command."""
    client = get_opensearch_client()

    if args.job_run_id:
        # Show details for specific job
        job = lookup_job(client, args.job_run_id)
        if not job:
            print(f"Error: Job {args.job_run_id} not found", file=sys.stderr)
            sys.exit(1)

        print(f"Job Run: {job.get('job_run_id')}")
        print(f"Job Name: {job.get('job_name')}")
        print(f"Timestamp: {job.get('timestamp')}")
        print(f"Status: {job.get('status')}")
        print()
        print("Quality Checks:")
        for check in job.get('quality_checks', []):
            symbol = '✗' if check.get('status') == 'RED' else '✓'
            print(f"  {symbol} {check.get('name')}: {check.get('value')} (threshold: {check.get('threshold')})")
        print()
        print("Metrics:")
        print(f"  Records Read: {job.get('records_read', 0):,}")
        print(f"  Records Written: {job.get('records_written', 0):,}")
        print(f"  Records Dropped: {job.get('records_dropped', 0):,}")
        print()
        print(f"To approve: dwh-approve {args.job_run_id} --reason \"your reason\"")
        print(f"To reject:  dwh-reject {args.job_run_id} --reason \"your reason\"")
    else:
        # List all pending jobs
        jobs = list_pending_jobs(client)

        if not jobs:
            print("No jobs pending approval")
            return

        print(f"PENDING APPROVALS ({len(jobs)} jobs)")
        print()
        for job in jobs:
            # Find first RED check
            red_check = next(
                (c for c in job.get('quality_checks', []) if c.get('status') == 'RED'),
                {}
            )
            check_summary = f"{red_check.get('name', '?')}: {red_check.get('value', '?')}" if red_check else ''

            print(f"  {job.get('job_run_id'):12}  {job.get('job_name'):20}  {job.get('timestamp')[:16]}  {check_summary}")


def main():
    parser = argparse.ArgumentParser(description='DWH Job Approval CLI')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # approve command
    approve_parser = subparsers.add_parser('approve', help='Approve a pending job')
    approve_parser.add_argument('job_run_id', help='Job run ID to approve')
    approve_parser.add_argument('--reason', '-r', required=True, help='Reason for approval')
    approve_parser.add_argument('--user', '-u', help='User making decision (default: from AWS identity)')
    approve_parser.set_defaults(func=cmd_approve)

    # reject command
    reject_parser = subparsers.add_parser('reject', help='Reject a pending job')
    reject_parser.add_argument('job_run_id', help='Job run ID to reject')
    reject_parser.add_argument('--reason', '-r', required=True, help='Reason for rejection')
    reject_parser.add_argument('--user', '-u', help='User making decision (default: from AWS identity)')
    reject_parser.set_defaults(func=cmd_reject)

    # pending command
    pending_parser = subparsers.add_parser('pending', help='List pending approvals')
    pending_parser.add_argument('job_run_id', nargs='?', help='Job run ID for details')
    pending_parser.set_defaults(func=cmd_pending)

    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
```

### Installation

```bash
# Install as CLI tool
pip install dwh-tools  # hypothetical package

# Or run directly
python -m dwh.tools.approval approve abc123 --reason "..."
```

## Infrastructure Requirements

### API Gateway + Lambda

```hcl
# API Gateway for approval endpoints
resource "aws_apigatewayv2_api" "approvals" {
  name          = "dwh-approvals-${var.environment}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_stage" "approvals" {
  api_id      = aws_apigatewayv2_api.approvals.id
  name        = "$default"
  auto_deploy = true
}

# Routes
resource "aws_apigatewayv2_route" "approve" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "GET /approvals/{job_run_id}/approve"
  target    = "integrations/${aws_apigatewayv2_integration.approval_lambda.id}"
}

resource "aws_apigatewayv2_route" "reject" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "GET /approvals/{job_run_id}/reject"
  target    = "integrations/${aws_apigatewayv2_integration.approval_lambda.id}"
}

resource "aws_apigatewayv2_route" "confirm" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "POST /approvals/{job_run_id}/confirm"
  target    = "integrations/${aws_apigatewayv2_integration.approval_lambda.id}"
}

# Lambda integration
resource "aws_apigatewayv2_integration" "approval_lambda" {
  api_id                 = aws_apigatewayv2_api.approvals.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.approval_api.invoke_arn
  payload_format_version = "2.0"
}

# Lambda function
resource "aws_lambda_function" "approval_api" {
  function_name = "dwh-approval-api-${var.environment}"
  handler       = "approval_api.handler"
  runtime       = "python3.11"

  environment {
    variables = {
      OPENSEARCH_ENDPOINT    = aws_opensearch_domain.job_metrics.endpoint
      SNS_TOPIC_ARN          = aws_sns_topic.job_approvals.arn
      APPROVAL_TOKEN_SECRET  = aws_secretsmanager_secret_version.approval_token.secret_string
      APPROVAL_TOKEN_TTL_HOURS = "72"
    }
  }
}

# Secret for token signing
resource "aws_secretsmanager_secret" "approval_token" {
  name = "dwh-approval-token-secret-${var.environment}"
}

resource "aws_secretsmanager_secret_version" "approval_token" {
  secret_id     = aws_secretsmanager_secret.approval_token.id
  secret_string = random_password.approval_token.result
}

resource "random_password" "approval_token" {
  length  = 32
  special = false
}
```

### SSM Parameters for CLI

```hcl
resource "aws_ssm_parameter" "opensearch_endpoint" {
  name  = "/dwh/opensearch/endpoint"
  type  = "String"
  value = aws_opensearch_domain.job_metrics.endpoint
}

resource "aws_ssm_parameter" "job_approvals_arn" {
  name  = "/dwh/sns/job-approvals-arn"
  type  = "String"
  value = aws_sns_topic.job_approvals.arn
}
```

## Approval Lambda Implementation

```python
"""
Lambda function for approval API endpoints.

Handles:
- GET /approvals/{job_run_id}/approve?token=xyz  → Show confirmation page
- GET /approvals/{job_run_id}/reject?token=xyz   → Show confirmation page
- POST /approvals/{job_run_id}/confirm           → Process decision
"""

import json
import os
import boto3
from datetime import datetime

# Import token utilities (from shared module)
from approval_tokens import generate_approval_token, validate_approval_token

OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']


def handler(event, context):
    """Main Lambda handler."""
    print(f"Event: {json.dumps(event)}")

    http_method = event.get('requestContext', {}).get('http', {}).get('method')
    path = event.get('rawPath', '')

    if http_method == 'GET' and '/approve' in path:
        return handle_approval_page(event, 'APPROVE')
    elif http_method == 'GET' and '/reject' in path:
        return handle_approval_page(event, 'REJECT')
    elif http_method == 'POST' and '/confirm' in path:
        return handle_confirm(event)
    else:
        return response(404, 'Not found')


def handle_approval_page(event, action: str):
    """Show confirmation page for approval/rejection."""
    job_run_id = event.get('pathParameters', {}).get('job_run_id')
    token = event.get('queryStringParameters', {}).get('token')

    if not token:
        return response(400, 'Missing token')

    # Validate token
    token_data = validate_approval_token(token)
    if not token_data:
        return html_response(400, error_page('Invalid or expired token'))

    if token_data['job_run_id'] != job_run_id:
        return html_response(400, error_page('Token does not match job'))

    if token_data['action'] != action:
        return html_response(400, error_page(f'Token is for {token_data["action"]}, not {action}'))

    # Look up job
    job = lookup_job(job_run_id)
    if not job:
        return html_response(404, error_page('Job not found'))

    if job.get('status') != 'PENDING_APPROVAL':
        return html_response(400, error_page(f'Job is not pending approval (status: {job.get("status")})'))

    # Render confirmation page
    html = confirmation_page(job, action, token)
    return html_response(200, html)


def handle_confirm(event):
    """Process the confirmation form submission."""
    job_run_id = event.get('pathParameters', {}).get('job_run_id')

    # Parse body
    body = json.loads(event.get('body', '{}'))
    token = body.get('token')
    action = body.get('action')
    reason = body.get('reason', '').strip()
    decided_by = body.get('decided_by', '').strip()

    if not token or not action or not reason or not decided_by:
        return html_response(400, error_page('Missing required fields'))

    # Validate token again
    token_data = validate_approval_token(token)
    if not token_data:
        return html_response(400, error_page('Invalid or expired token'))

    if token_data['job_run_id'] != job_run_id or token_data['action'] != action:
        return html_response(400, error_page('Token mismatch'))

    # Look up job
    job = lookup_job(job_run_id)
    if not job:
        return html_response(404, error_page('Job not found'))

    if job.get('status') != 'PENDING_APPROVAL':
        return html_response(400, error_page(f'Job is no longer pending approval'))

    # Publish decision
    publish_decision(
        job_run_id=job_run_id,
        job_name=job.get('job_name'),
        decision='APPROVED' if action == 'APPROVE' else 'REJECTED',
        reason=reason,
        decided_by=decided_by
    )

    # Return success page
    html = success_page(job, action)
    return html_response(200, html)


def lookup_job(job_run_id: str) -> dict | None:
    """Look up job in OpenSearch."""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth

    session = boto3.Session()
    credentials = session.get_credentials()
    region = os.environ.get('AWS_REGION', 'us-west-1')

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )

    client = OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )

    response = client.search(
        index='job-events',
        body={'query': {'term': {'job_run_id': job_run_id}}}
    )

    hits = response['hits']['hits']
    return hits[0]['_source'] if hits else None


def publish_decision(job_run_id: str, job_name: str, decision: str, reason: str, decided_by: str):
    """Publish approval decision to SNS."""
    sns = boto3.client('sns')

    message = {
        'event_type': 'approval_decision',
        'job_name': job_name,
        'job_run_id': job_run_id,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'decision': decision,
        'decided_by': decided_by,
        'reason': reason
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes={
            'decision': {'DataType': 'String', 'StringValue': decision}
        }
    )


def response(status_code: int, message: str):
    return {
        'statusCode': status_code,
        'body': json.dumps({'message': message}),
        'headers': {'Content-Type': 'application/json'}
    }


def html_response(status_code: int, html: str):
    return {
        'statusCode': status_code,
        'body': html,
        'headers': {'Content-Type': 'text/html'}
    }


def confirmation_page(job: dict, action: str, token: str) -> str:
    """Generate confirmation page HTML."""
    action_text = 'Approve' if action == 'APPROVE' else 'Reject'
    action_color = '#28a745' if action == 'APPROVE' else '#dc3545'

    # Format quality checks
    checks_html = ''
    for check in job.get('quality_checks', []):
        symbol = '&#10007;' if check.get('status') == 'RED' else '&#10003;'
        color = '#dc3545' if check.get('status') == 'RED' else '#28a745'
        checks_html += f'''
            <div style="color: {color}; margin: 5px 0;">
                {symbol} {check.get('name')}: {check.get('value')} (threshold: {check.get('threshold')})
            </div>
        '''

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>{action_text} Job - DWH Pipeline</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   max-width: 600px; margin: 50px auto; padding: 20px; }}
            .card {{ border: 1px solid #ddd; border-radius: 8px; padding: 20px; }}
            .header {{ font-size: 24px; margin-bottom: 20px; }}
            .field {{ margin: 10px 0; }}
            .label {{ font-weight: bold; color: #666; }}
            textarea {{ width: 100%; height: 80px; margin: 10px 0; padding: 10px;
                       border: 1px solid #ddd; border-radius: 4px; }}
            input[type="email"] {{ width: 100%; padding: 10px; border: 1px solid #ddd;
                                   border-radius: 4px; margin: 10px 0; }}
            .buttons {{ margin-top: 20px; }}
            button {{ padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;
                     font-size: 16px; margin-right: 10px; }}
            .primary {{ background: {action_color}; color: white; }}
            .secondary {{ background: #6c757d; color: white; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">{action_text} Job Run</div>

            <div class="field">
                <span class="label">Job:</span> {job.get('job_name')}
            </div>
            <div class="field">
                <span class="label">Run ID:</span> {job.get('job_run_id')}
            </div>
            <div class="field">
                <span class="label">Quality Status:</span>
                <span style="color: #dc3545; font-weight: bold;">{job.get('quality_status')}</span>
            </div>

            <div class="field">
                <span class="label">Quality Checks:</span>
                {checks_html}
            </div>

            <form method="POST" action="/approvals/{job.get('job_run_id')}/confirm">
                <input type="hidden" name="token" value="{token}">
                <input type="hidden" name="action" value="{action}">

                <div class="field">
                    <span class="label">Reason for {action.lower()}ion: (required)</span>
                    <textarea name="reason" required placeholder="Explain why this decision is appropriate..."></textarea>
                </div>

                <div class="field">
                    <span class="label">Your email:</span>
                    <input type="email" name="decided_by" required placeholder="you@company.com">
                </div>

                <div class="buttons">
                    <button type="button" class="secondary" onclick="window.close()">Cancel</button>
                    <button type="submit" class="primary">Confirm {action_text}</button>
                </div>
            </form>
        </div>
    </body>
    </html>
    '''


def success_page(job: dict, action: str) -> str:
    """Generate success page HTML."""
    action_text = 'Approved' if action == 'APPROVE' else 'Rejected'
    message = 'Downstream processing will resume automatically.' if action == 'APPROVE' else 'Artifacts should be cleaned up and job re-run.'

    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Job {action_text} - DWH Pipeline</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .success {{ color: #28a745; font-size: 48px; }}
            .message {{ font-size: 18px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="success">&#10003;</div>
        <h1>Job {action_text}</h1>
        <p class="message">
            Job <strong>{job.get('job_name')}</strong> ({job.get('job_run_id')}) has been {action_text.lower()}.
        </p>
        <p>{message}</p>
    </body>
    </html>
    '''


def error_page(message: str) -> str:
    """Generate error page HTML."""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Error - DWH Pipeline</title>
        <style>
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                   max-width: 600px; margin: 50px auto; padding: 20px; text-align: center; }}
            .error {{ color: #dc3545; font-size: 48px; }}
        </style>
    </head>
    <body>
        <div class="error">&#10007;</div>
        <h1>Error</h1>
        <p>{message}</p>
    </body>
    </html>
    '''
```

## Summary

| Method | Use Case | Authentication |
|--------|----------|----------------|
| Email Links | Primary - anyone can approve | Signed token (72h TTL) |
| CLI Tool | Developers - fast approval | AWS credentials |
| Dashboard | Future - full context | SSO/Dashboard login |
| Slack | Future - team collaboration | Slack identity |

## Open Questions

- [ ] Should tokens be single-use (invalidated after first click)?
- [ ] Should we require additional authentication (e.g., SSO redirect)?
- [ ] Should approval emails go to a specific group or job owner?
- [ ] How long should approvals be valid (72 hours default)?
- [ ] Should we support delegation (approve on behalf of)?
