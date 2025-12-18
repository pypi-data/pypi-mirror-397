# OpenSearch Dashboard Approval Solution

> **⚠️ NOT YET IMPLEMENTED**
>
> This document describes a **proposed future design** for an OpenSearch-based approval dashboard.
> The features described here (dashboard visualizations, embedded forms, approval API integration)
> have NOT been implemented yet. This document is retained for future reference.
>
> **Current state:** Job events are indexed to OpenSearch by the job_events_indexer Lambda,
> but no approval dashboard or embedded forms have been set up.

This document describes the OpenSearch Dashboards-based approval workflow for jobs with quality failures. This is the recommended approach for POC due to its visual appeal and minimal infrastructure requirements.

## Why OpenSearch Dashboards for Approvals?

1. **Already deployed** - OpenSearch is already part of the infrastructure
2. **Visual context** - See metrics, trends, and quality details while deciding
3. **Audit trail built-in** - All actions logged in OpenSearch
4. **No additional infrastructure** - No API Gateway, no separate Lambda for UI
5. **Demo-friendly** - Visually compelling for stakeholders

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     OpenSearch Dashboards                            │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  Pending Approvals Dashboard                 │    │
│  │                                                              │    │
│  │  ┌──────────────────────────────────────────────────────┐   │    │
│  │  │  PENDING APPROVALS (2)                               │   │    │
│  │  │                                                      │   │    │
│  │  │  ┌────────────────────────────────────────────────┐  │   │    │
│  │  │  │ transform_images | abc123 | drop_rate: 12%    │  │   │    │
│  │  │  │ 2024-01-15 10:30 | Records: 88,000            │  │   │    │
│  │  │  └────────────────────────────────────────────────┘  │   │    │
│  │  │                                                      │   │    │
│  │  │  ┌────────────────────────────────────────────────┐  │   │    │
│  │  │  │ load_customers | def456 | null_rate: 8%       │  │   │    │
│  │  │  │ 2024-01-15 11:45 | Records: 125,000           │  │   │    │
│  │  │  └────────────────────────────────────────────────┘  │   │    │
│  │  └──────────────────────────────────────────────────────┘   │    │
│  │                                                              │    │
│  │  Click job to view details and approve/reject                │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│                              │                                       │
│                              ▼                                       │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Job Detail View                           │    │
│  │                                                              │    │
│  │  Job: transform_images                                       │    │
│  │  Run ID: abc123                                              │    │
│  │  Status: PENDING_APPROVAL                                    │    │
│  │                                                              │    │
│  │  ┌─────────────────────┐  ┌─────────────────────┐           │    │
│  │  │   Quality Checks    │  │      Metrics        │           │    │
│  │  │                     │  │                     │           │    │
│  │  │  ✗ drop_rate: 12%   │  │  Read:    100,000   │           │    │
│  │  │    threshold: 10%   │  │  Written:  88,000   │           │    │
│  │  │                     │  │  Dropped:  12,000   │           │    │
│  │  │  ✓ null_rate: 2%    │  │  Duration: 2m 30s   │           │    │
│  │  │    threshold: 5%    │  │                     │           │    │
│  │  └─────────────────────┘  └─────────────────────┘           │    │
│  │                                                              │    │
│  │  ┌─────────────────────────────────────────────────────┐    │    │
│  │  │  Historical Drop Rate (last 30 days)                │    │    │
│  │  │  ▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁██ ← Today: 12%      │    │    │
│  │  └─────────────────────────────────────────────────────┘    │    │
│  │                                                              │    │
│  │  [View Artifacts in S3]                                      │    │
│  │                                                              │    │
│  │  ─────────────────────────────────────────────────────────   │    │
│  │                                                              │    │
│  │  Decision:  ○ Approve  ○ Reject                              │    │
│  │                                                              │    │
│  │  Reason: [________________________________________]          │    │
│  │                                                              │    │
│  │  Your Name: [____________________]                           │    │
│  │                                                              │    │
│  │  [ Submit Decision ]                                         │    │
│  │                                                              │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Approval API Lambda                               │
│                                                                      │
│  POST /approvals                                                     │
│  {                                                                   │
│    "job_run_id": "abc123",                                          │
│    "decision": "APPROVED",                                           │
│    "reason": "Known vendor issue",                                   │
│    "decided_by": "jsmith"                                            │
│  }                                                                   │
│                                                                      │
│  → Publishes to job_approvals SNS topic                             │
│  → Updates OpenSearch document                                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Implementation Components

### 1. OpenSearch Index Schema

Update the `job-events` index to support the approval workflow:

```json
{
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "event_type": {"type": "keyword"},

            "job_name": {"type": "keyword"},
            "job_run_id": {"type": "keyword"},
            "status": {"type": "keyword"},
            "failure_type": {"type": "keyword"},

            "quality_status": {"type": "keyword"},
            "quality_checks": {
                "type": "nested",
                "properties": {
                    "name": {"type": "keyword"},
                    "status": {"type": "keyword"},
                    "value": {"type": "float"},
                    "threshold": {"type": "float"}
                }
            },

            "artifacts_available": {"type": "boolean"},
            "artifacts": {
                "type": "object",
                "properties": {
                    "nautilus": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "keyword"},
                            "records": {"type": "long"},
                            "bytes": {"type": "long"}
                        }
                    },
                    "savedproject": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "keyword"},
                            "records": {"type": "long"},
                            "bytes": {"type": "long"}
                        }
                    }
                }
            },

            "records_read": {"type": "long"},
            "records_written": {"type": "long"},
            "records_dropped": {"type": "long"},
            "bytes_written": {"type": "long"},
            "duration_seconds": {"type": "float"},

            "approval_status": {"type": "keyword"},
            "approval_decision": {"type": "keyword"},
            "approved_by": {"type": "keyword"},
            "approval_reason": {"type": "text"},
            "approval_timestamp": {"type": "date"}
        }
    }
}
```

### 2. Saved Searches

#### Pending Approvals Search

```json
{
    "title": "Pending Approvals",
    "description": "Jobs awaiting human approval",
    "query": {
        "bool": {
            "must": [
                {"term": {"status": "PENDING_APPROVAL"}}
            ]
        }
    },
    "sort": [{"timestamp": "desc"}],
    "columns": [
        "job_name",
        "job_run_id",
        "timestamp",
        "quality_status",
        "records_written",
        "records_dropped"
    ]
}
```

#### Recently Approved/Rejected Search

```json
{
    "title": "Recent Approval Decisions",
    "description": "Jobs that were approved or rejected in the last 7 days",
    "query": {
        "bool": {
            "must": [
                {"exists": {"field": "approval_decision"}},
                {"range": {"approval_timestamp": {"gte": "now-7d"}}}
            ]
        }
    },
    "sort": [{"approval_timestamp": "desc"}],
    "columns": [
        "job_name",
        "job_run_id",
        "approval_decision",
        "approved_by",
        "approval_timestamp",
        "approval_reason"
    ]
}
```

### 3. Dashboard Visualizations

#### Visualization 1: Pending Approvals Count (Metric)

```json
{
    "title": "Pending Approvals",
    "type": "metric",
    "params": {
        "metric": {
            "accessor": 0,
            "format": {"id": "number"},
            "style": {
                "bgColor": "#ffc107",
                "fontSize": 60
            }
        }
    },
    "aggs": [
        {
            "id": "1",
            "type": "count",
            "schema": "metric"
        }
    ],
    "filter": {
        "term": {"status": "PENDING_APPROVAL"}
    }
}
```

#### Visualization 2: Pending Approvals Table

```json
{
    "title": "Jobs Awaiting Approval",
    "type": "table",
    "params": {
        "perPage": 10,
        "showPartialRows": false,
        "showTotal": true
    },
    "aggs": [
        {
            "id": "1",
            "type": "terms",
            "schema": "bucket",
            "params": {
                "field": "job_run_id",
                "size": 100,
                "order": "desc",
                "orderBy": "_key"
            }
        },
        {
            "id": "2",
            "type": "top_hits",
            "schema": "metric",
            "params": {
                "field": "job_name",
                "size": 1
            }
        }
    ]
}
```

#### Visualization 3: Quality Check Failure Distribution (Pie Chart)

```json
{
    "title": "Failure Reasons",
    "type": "pie",
    "params": {
        "type": "pie",
        "addTooltip": true,
        "addLegend": true
    },
    "aggs": [
        {
            "id": "1",
            "type": "count",
            "schema": "metric"
        },
        {
            "id": "2",
            "type": "terms",
            "schema": "segment",
            "params": {
                "field": "quality_checks.name",
                "size": 10
            }
        }
    ],
    "filter": {
        "nested": {
            "path": "quality_checks",
            "query": {
                "term": {"quality_checks.status": "RED"}
            }
        }
    }
}
```

#### Visualization 4: Historical Drop Rate Trend (Line Chart)

```json
{
    "title": "Drop Rate Over Time",
    "type": "line",
    "params": {
        "type": "line",
        "addTimeMarker": true,
        "addLegend": true
    },
    "aggs": [
        {
            "id": "1",
            "type": "avg",
            "schema": "metric",
            "params": {
                "field": "drop_rate"
            }
        },
        {
            "id": "2",
            "type": "date_histogram",
            "schema": "segment",
            "params": {
                "field": "timestamp",
                "interval": "1d"
            }
        }
    ]
}
```

### 4. Approval Form (Custom Visualization)

OpenSearch Dashboards supports custom visualizations via plugins. For the POC, we'll use a simpler approach: **Vega visualization** with a form that posts to our API.

#### Vega Approval Form

```json
{
    "$schema": "https://vega.github.io/schema/vega/v5.json",
    "title": "Approval Action",
    "width": 400,
    "height": 300,
    "padding": 20,

    "signals": [
        {
            "name": "jobRunId",
            "value": "",
            "bind": {"input": "text", "placeholder": "Enter Job Run ID"}
        },
        {
            "name": "decision",
            "value": "APPROVE",
            "bind": {"input": "radio", "options": ["APPROVE", "REJECT"]}
        },
        {
            "name": "reason",
            "value": "",
            "bind": {"input": "text", "placeholder": "Reason for decision"}
        },
        {
            "name": "decidedBy",
            "value": "",
            "bind": {"input": "text", "placeholder": "Your name/email"}
        }
    ],

    "marks": [
        {
            "type": "text",
            "encode": {
                "enter": {
                    "x": {"value": 10},
                    "y": {"value": 20},
                    "text": {"value": "Submit approval via API or CLI"},
                    "fontSize": {"value": 14}
                }
            }
        }
    ]
}
```

**Note:** Vega has limited form capabilities. For a true interactive form, we'll use one of these approaches:

### 5. Approval Approaches (Choose One)

#### Option A: External Approval Page (Linked from Dashboard)

Add a Markdown visualization with a link:

```markdown
## Submit Approval

To approve or reject a job, use one of these methods:

### Web Form
[Open Approval Form](https://dwh-api.company.com/approvals/form)

### CLI
```bash
dwh-approve <job_run_id> --reason "your reason"
dwh-reject <job_run_id> --reason "your reason"
```

### API
```bash
curl -X POST https://dwh-api.company.com/approvals \
  -H "Content-Type: application/json" \
  -d '{
    "job_run_id": "<job_run_id>",
    "decision": "APPROVED",
    "reason": "your reason",
    "decided_by": "your.email@company.com"
  }'
```
```

#### Option B: OpenSearch Alerting Plugin (Recommended for POC)

Use the OpenSearch Alerting plugin to create an "action" that can be triggered:

1. Create a **Monitor** that watches for PENDING_APPROVAL jobs
2. Create an **Action** with a webhook destination
3. The webhook calls the approval API

This doesn't give a form, but shows alerts in the dashboard.

#### Option C: Custom OpenSearch Plugin (Future)

Build a custom OpenSearch Dashboards plugin with a proper React form. This is more work but provides the best UX.

#### Option D: Embedded iframe (Quick POC Solution) ✓

Embed a simple HTML form via iframe in the dashboard:

```html
<!-- Hosted at: https://dwh-api.company.com/approvals/embed-form -->
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: -apple-system, sans-serif; padding: 20px; }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none;
                 border-radius: 4px; cursor: pointer; }
        button:hover { background: #0056b3; }
        .success { color: #28a745; }
        .error { color: #dc3545; }
    </style>
</head>
<body>
    <h3>Submit Approval Decision</h3>

    <form id="approvalForm">
        <div class="form-group">
            <label>Job Run ID:</label>
            <input type="text" id="jobRunId" required placeholder="e.g., abc123">
        </div>

        <div class="form-group">
            <label>Decision:</label>
            <select id="decision" required>
                <option value="">-- Select --</option>
                <option value="APPROVED">Approve - Continue downstream</option>
                <option value="REJECTED">Reject - Requires rerun</option>
            </select>
        </div>

        <div class="form-group">
            <label>Reason:</label>
            <textarea id="reason" required rows="3"
                      placeholder="Explain why this decision is appropriate..."></textarea>
        </div>

        <div class="form-group">
            <label>Your Name/Email:</label>
            <input type="text" id="decidedBy" required placeholder="jsmith@company.com">
        </div>

        <button type="submit">Submit Decision</button>
    </form>

    <div id="result" style="margin-top: 20px;"></div>

    <script>
        document.getElementById('approvalForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const data = {
                job_run_id: document.getElementById('jobRunId').value,
                decision: document.getElementById('decision').value,
                reason: document.getElementById('reason').value,
                decided_by: document.getElementById('decidedBy').value
            };

            try {
                const response = await fetch('/approvals', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    document.getElementById('result').innerHTML =
                        '<p class="success">✓ Decision submitted successfully!</p>';
                    document.getElementById('approvalForm').reset();
                } else {
                    document.getElementById('result').innerHTML =
                        `<p class="error">✗ Error: ${result.message}</p>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML =
                    `<p class="error">✗ Error: ${error.message}</p>`;
            }
        });
    </script>
</body>
</html>
```

Then in OpenSearch Dashboards, add a **Markdown** visualization:

```markdown
<iframe src="https://dwh-api.company.com/approvals/embed-form"
        width="100%" height="400" frameborder="0"></iframe>
```

**Note:** May require CSP header configuration on OpenSearch.

## Complete Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DWH Pipeline - Approval Dashboard                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                  │
│  │   PENDING       │  │   APPROVED      │  │   REJECTED      │                  │
│  │                 │  │   (7 days)      │  │   (7 days)      │                  │
│  │      2          │  │      15         │  │      3          │                  │
│  │                 │  │                 │  │                 │                  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                  │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  JOBS AWAITING APPROVAL                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │ Job Name          │ Run ID   │ Timestamp        │ Quality │ Written     │  │
│  ├───────────────────┼──────────┼──────────────────┼─────────┼─────────────┤  │
│  │ transform_images  │ abc123   │ 2024-01-15 10:30 │ RED     │ 88,000      │  │
│  │ load_customers    │ def456   │ 2024-01-15 11:45 │ RED     │ 125,000     │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
├──────────────────────────────────────┬──────────────────────────────────────────┤
│                                      │                                          │
│  FAILURE REASONS (This Week)         │  DROP RATE TREND (30 Days)               │
│  ┌────────────────────────────────┐  │  ┌────────────────────────────────────┐  │
│  │         ████████               │  │  │                              ██    │  │
│  │  drop_rate ████████  65%       │  │  │                             ███    │  │
│  │            ████                │  │  │  ▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂▁▁▂▁▂████    │  │
│  │  null_rate ████      25%       │  │  │  ─────────────────────────────────  │  │
│  │            ██                  │  │  │  Jan 1                      Jan 15  │  │
│  │  other     ██        10%       │  │  └────────────────────────────────────┘  │
│  └────────────────────────────────┘  │                                          │
│                                      │                                          │
├──────────────────────────────────────┴──────────────────────────────────────────┤
│                                                                                  │
│  SUBMIT APPROVAL DECISION                                                        │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │                                                                           │  │
│  │  Job Run ID: [abc123_____________]                                        │  │
│  │                                                                           │  │
│  │  Decision:   ○ Approve - Continue downstream processing                   │  │
│  │              ○ Reject - Requires source fix and rerun                     │  │
│  │                                                                           │  │
│  │  Reason:     [Known vendor data issue in batch 2024-01-15.___________]   │  │
│  │              [Acceptable for this run._______________________________]   │  │
│  │                                                                           │  │
│  │  Your Name:  [jsmith@company.com_____]                                    │  │
│  │                                                                           │  │
│  │  [ Submit Decision ]                                                      │  │
│  │                                                                           │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                  │
│  RECENT DECISIONS                                                                │
│  ┌───────────────────────────────────────────────────────────────────────────┐  │
│  │ Job Name          │ Run ID   │ Decision │ By           │ When            │  │
│  ├───────────────────┼──────────┼──────────┼──────────────┼─────────────────┤  │
│  │ transform_images  │ xyz789   │ APPROVED │ jsmith       │ 2024-01-14 16:00│  │
│  │ load_inventory    │ qrs456   │ REJECTED │ mjones       │ 2024-01-14 11:30│  │
│  │ transform_images  │ lmn123   │ APPROVED │ jsmith       │ 2024-01-13 09:15│  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Approval API Lambda

Simple Lambda that receives form submissions and publishes to SNS:

```python
"""
Approval API Lambda - handles approval submissions from dashboard.

Endpoints:
- POST /approvals - Submit approval decision
- GET /approvals/embed-form - Serve embedded form HTML
- GET /approvals/pending - List pending approvals (for form autocomplete)
"""

import json
import os
import boto3
from datetime import datetime

SNS_TOPIC_ARN = os.environ['JOB_APPROVALS_SNS_ARN']
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']


def handler(event, context):
    """Main Lambda handler for API Gateway."""
    print(f"Event: {json.dumps(event)}")

    http_method = event.get('requestContext', {}).get('http', {}).get('method', '')
    path = event.get('rawPath', '')

    if http_method == 'POST' and path == '/approvals':
        return handle_submit_approval(event)
    elif http_method == 'GET' and path == '/approvals/embed-form':
        return handle_embed_form()
    elif http_method == 'GET' and path == '/approvals/pending':
        return handle_list_pending()
    elif http_method == 'OPTIONS':
        return cors_response(200, {})
    else:
        return response(404, {'message': 'Not found'})


def handle_submit_approval(event):
    """Process approval submission."""
    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return response(400, {'message': 'Invalid JSON'})

    # Validate required fields
    required = ['job_run_id', 'decision', 'reason', 'decided_by']
    missing = [f for f in required if not body.get(f)]
    if missing:
        return response(400, {'message': f'Missing required fields: {missing}'})

    job_run_id = body['job_run_id']
    decision = body['decision'].upper()
    reason = body['reason']
    decided_by = body['decided_by']

    if decision not in ('APPROVED', 'REJECTED'):
        return response(400, {'message': 'Decision must be APPROVED or REJECTED'})

    # Verify job exists and is pending
    job = lookup_job(job_run_id)
    if not job:
        return response(404, {'message': f'Job {job_run_id} not found'})

    if job.get('status') != 'PENDING_APPROVAL':
        return response(400, {
            'message': f'Job {job_run_id} is not pending approval (status: {job.get("status")})'
        })

    # Publish to SNS
    publish_approval_decision(
        job_run_id=job_run_id,
        job_name=job.get('job_name'),
        decision=decision,
        reason=reason,
        decided_by=decided_by
    )

    # Update OpenSearch document directly (for immediate UI feedback)
    update_job_approval_status(
        job_run_id=job_run_id,
        decision=decision,
        reason=reason,
        decided_by=decided_by
    )

    return response(200, {
        'message': 'Approval decision submitted',
        'job_run_id': job_run_id,
        'decision': decision
    })


def handle_embed_form():
    """Return the embedded approval form HTML."""
    html = get_embed_form_html()
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        },
        'body': html
    }


def handle_list_pending():
    """Return list of pending approvals for form autocomplete."""
    jobs = list_pending_jobs()
    return response(200, {'jobs': jobs})


def lookup_job(job_run_id: str) -> dict | None:
    """Look up job in OpenSearch."""
    client = get_opensearch_client()

    result = client.search(
        index='job-events',
        body={
            'query': {'term': {'job_run_id': job_run_id}},
            'size': 1
        }
    )

    hits = result['hits']['hits']
    return hits[0]['_source'] if hits else None


def list_pending_jobs() -> list:
    """List all pending approval jobs."""
    client = get_opensearch_client()

    result = client.search(
        index='job-events',
        body={
            'query': {'term': {'status': 'PENDING_APPROVAL'}},
            'sort': [{'timestamp': 'desc'}],
            'size': 100,
            '_source': ['job_run_id', 'job_name', 'timestamp', 'quality_status']
        }
    )

    return [hit['_source'] for hit in result['hits']['hits']]


def publish_approval_decision(job_run_id: str, job_name: str, decision: str,
                               reason: str, decided_by: str):
    """Publish approval decision to SNS topic."""
    sns = boto3.client('sns')

    message = {
        'event_type': 'approval_decision',
        'job_run_id': job_run_id,
        'job_name': job_name,
        'decision': decision,
        'reason': reason,
        'decided_by': decided_by,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=json.dumps(message),
        MessageAttributes={
            'decision': {'DataType': 'String', 'StringValue': decision}
        }
    )

    print(f"Published approval decision: {job_run_id} -> {decision}")


def update_job_approval_status(job_run_id: str, decision: str, reason: str, decided_by: str):
    """Update job document in OpenSearch with approval info."""
    client = get_opensearch_client()

    # Find document ID
    result = client.search(
        index='job-events',
        body={
            'query': {'term': {'job_run_id': job_run_id}},
            'size': 1
        }
    )

    if not result['hits']['hits']:
        return

    doc_id = result['hits']['hits'][0]['_id']

    # Update document
    client.update(
        index='job-events',
        id=doc_id,
        body={
            'doc': {
                'status': 'APPROVED' if decision == 'APPROVED' else 'REJECTED',
                'approval_status': decision,
                'approval_decision': decision,
                'approved_by': decided_by,
                'approval_reason': reason,
                'approval_timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        }
    )

    print(f"Updated OpenSearch document: {doc_id}")


def get_opensearch_client():
    """Create OpenSearch client with AWS auth."""
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

    return OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def get_embed_form_html() -> str:
    """Return the embedded form HTML."""
    return '''<!DOCTYPE html>
<html>
<head>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            padding: 15px;
            margin: 0;
            background: #f8f9fa;
        }
        h3 { margin-top: 0; color: #333; }
        .form-group { margin-bottom: 12px; }
        label { display: block; margin-bottom: 4px; font-weight: 600; color: #555; font-size: 13px; }
        input, select, textarea {
            width: 100%;
            padding: 8px 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #007bff;
            box-shadow: 0 0 0 2px rgba(0,123,255,0.1);
        }
        textarea { resize: vertical; min-height: 60px; }
        button {
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        button:hover { background: #0056b3; }
        button:disabled { background: #ccc; cursor: not-allowed; }
        .success { color: #28a745; font-weight: 600; }
        .error { color: #dc3545; font-weight: 600; }
        .pending-list {
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-height: 150px;
            overflow-y: auto;
            margin-bottom: 15px;
        }
        .pending-item {
            padding: 8px 10px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            font-size: 13px;
        }
        .pending-item:hover { background: #f0f7ff; }
        .pending-item:last-child { border-bottom: none; }
        .pending-item .job-name { font-weight: 600; }
        .pending-item .job-id { color: #666; font-family: monospace; }
    </style>
</head>
<body>
    <h3>Submit Approval Decision</h3>

    <div id="pendingJobs" class="pending-list" style="display:none;">
        <div style="padding: 8px 10px; color: #666; font-size: 12px;">Click to select:</div>
    </div>

    <form id="approvalForm">
        <div class="form-group">
            <label>Job Run ID:</label>
            <input type="text" id="jobRunId" required placeholder="e.g., abc123">
        </div>

        <div class="form-group">
            <label>Decision:</label>
            <select id="decision" required>
                <option value="">-- Select Decision --</option>
                <option value="APPROVED">✓ Approve - Continue downstream processing</option>
                <option value="REJECTED">✗ Reject - Requires source fix and rerun</option>
            </select>
        </div>

        <div class="form-group">
            <label>Reason:</label>
            <textarea id="reason" required rows="2"
                      placeholder="Explain why this decision is appropriate..."></textarea>
        </div>

        <div class="form-group">
            <label>Your Name/Email:</label>
            <input type="text" id="decidedBy" required placeholder="jsmith@company.com">
        </div>

        <button type="submit" id="submitBtn">Submit Decision</button>
    </form>

    <div id="result" style="margin-top: 15px;"></div>

    <script>
        // Load pending jobs on page load
        async function loadPendingJobs() {
            try {
                const response = await fetch('/approvals/pending');
                const data = await response.json();

                if (data.jobs && data.jobs.length > 0) {
                    const container = document.getElementById('pendingJobs');
                    container.style.display = 'block';

                    data.jobs.forEach(job => {
                        const div = document.createElement('div');
                        div.className = 'pending-item';
                        div.innerHTML = `
                            <span class="job-name">${job.job_name}</span>
                            <span class="job-id">${job.job_run_id}</span>
                        `;
                        div.onclick = () => {
                            document.getElementById('jobRunId').value = job.job_run_id;
                        };
                        container.appendChild(div);
                    });
                }
            } catch (e) {
                console.log('Could not load pending jobs:', e);
            }
        }

        loadPendingJobs();

        document.getElementById('approvalForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitBtn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Submitting...';

            const data = {
                job_run_id: document.getElementById('jobRunId').value,
                decision: document.getElementById('decision').value,
                reason: document.getElementById('reason').value,
                decided_by: document.getElementById('decidedBy').value
            };

            try {
                const response = await fetch('/approvals', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (response.ok) {
                    document.getElementById('result').innerHTML =
                        `<p class="success">✓ ${result.decision} - Decision submitted successfully!</p>`;
                    document.getElementById('approvalForm').reset();

                    // Remove the approved job from pending list
                    const items = document.querySelectorAll('.pending-item');
                    items.forEach(item => {
                        if (item.textContent.includes(data.job_run_id)) {
                            item.remove();
                        }
                    });
                } else {
                    document.getElementById('result').innerHTML =
                        `<p class="error">✗ Error: ${result.message}</p>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML =
                    `<p class="error">✗ Error: ${error.message}</p>`;
            } finally {
                submitBtn.disabled = false;
                submitBtn.textContent = 'Submit Decision';
            }
        });
    </script>
</body>
</html>'''


def response(status_code: int, body: dict):
    """Return JSON response with CORS headers."""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': json.dumps(body)
    }


def cors_response(status_code: int, body: dict):
    """Return CORS preflight response."""
    return {
        'statusCode': status_code,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type'
        },
        'body': ''
    }
```

## Infrastructure (Terraform)

```hcl
# API Gateway for approval endpoints
resource "aws_apigatewayv2_api" "approvals" {
  name          = "${local.resource_prefix}-approvals-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_headers = ["Content-Type"]
    max_age       = 300
  }

  tags = local.tags
}

resource "aws_apigatewayv2_stage" "approvals" {
  api_id      = aws_apigatewayv2_api.approvals.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_gateway.arn
    format = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      responseLength = "$context.responseLength"
    })
  }
}

# Routes
resource "aws_apigatewayv2_route" "approvals_post" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "POST /approvals"
  target    = "integrations/${aws_apigatewayv2_integration.approval_lambda.id}"
}

resource "aws_apigatewayv2_route" "approvals_form" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "GET /approvals/embed-form"
  target    = "integrations/${aws_apigatewayv2_integration.approval_lambda.id}"
}

resource "aws_apigatewayv2_route" "approvals_pending" {
  api_id    = aws_apigatewayv2_api.approvals.id
  route_key = "GET /approvals/pending"
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
  function_name = "${local.resource_prefix}-approval-api"
  handler       = "approval_api.handler"
  runtime       = "python3.11"
  timeout       = 30
  memory_size   = 256

  filename         = data.archive_file.approval_lambda.output_path
  source_code_hash = data.archive_file.approval_lambda.output_base64sha256

  role = aws_iam_role.approval_lambda.arn

  environment {
    variables = {
      OPENSEARCH_ENDPOINT     = aws_opensearch_domain.job_metrics.endpoint
      JOB_APPROVALS_SNS_ARN   = aws_sns_topic.job_approvals.arn
    }
  }

  layers = [
    aws_lambda_layer_version.opensearch_py.arn
  ]

  tags = local.tags
}

# Lambda permission for API Gateway
resource "aws_lambda_permission" "approval_api" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.approval_api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.approvals.execution_arn}/*/*"
}

# IAM role for Lambda
resource "aws_iam_role" "approval_lambda" {
  name = "${local.resource_prefix}-approval-lambda-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = local.tags
}

# Lambda policies
resource "aws_iam_role_policy" "approval_lambda_logs" {
  name = "logs"
  role = aws_iam_role.approval_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      Resource = "arn:aws:logs:*:*:*"
    }]
  })
}

resource "aws_iam_role_policy" "approval_lambda_opensearch" {
  name = "opensearch"
  role = aws_iam_role.approval_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Action = [
        "es:ESHttpGet",
        "es:ESHttpPost",
        "es:ESHttpPut"
      ]
      Resource = "${aws_opensearch_domain.job_metrics.arn}/*"
    }]
  })
}

resource "aws_iam_role_policy" "approval_lambda_sns" {
  name = "sns"
  role = aws_iam_role.approval_lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "sns:Publish"
      Resource = aws_sns_topic.job_approvals.arn
    }]
  })
}

# Output the API endpoint
output "approval_api_endpoint" {
  value = aws_apigatewayv2_api.approvals.api_endpoint
}
```

## Dashboard Setup Script

Script to create the dashboard and visualizations in OpenSearch:

```python
#!/usr/bin/env python3
"""
Script to set up the Approval Dashboard in OpenSearch Dashboards.

Run this after deploying the infrastructure to create:
- Saved searches
- Visualizations
- Dashboard
"""

import json
import os
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


def get_client():
    """Create OpenSearch client."""
    session = boto3.Session()
    credentials = session.get_credentials()
    region = os.environ.get('AWS_REGION', 'us-west-1')
    endpoint = os.environ['OPENSEARCH_ENDPOINT']

    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        region,
        'es',
        session_token=credentials.token
    )

    return OpenSearch(
        hosts=[{'host': endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def create_index_pattern(client):
    """Create index pattern for job-events."""
    client.index(
        index='.kibana',
        id='index-pattern:job-events',
        body={
            'type': 'index-pattern',
            'index-pattern': {
                'title': 'job-events',
                'timeFieldName': 'timestamp'
            }
        }
    )
    print("Created index pattern: job-events")


def create_saved_searches(client):
    """Create saved searches."""
    # Pending approvals
    client.index(
        index='.kibana',
        id='search:pending-approvals',
        body={
            'type': 'search',
            'search': {
                'title': 'Pending Approvals',
                'description': 'Jobs awaiting human approval',
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': 'job-events',
                        'query': {
                            'bool': {
                                'must': [{'term': {'status': 'PENDING_APPROVAL'}}]
                            }
                        },
                        'sort': [{'timestamp': 'desc'}]
                    })
                },
                'columns': ['job_name', 'job_run_id', 'timestamp', 'quality_status', 'records_written']
            }
        }
    )
    print("Created saved search: Pending Approvals")


def create_visualizations(client, api_endpoint: str):
    """Create visualizations."""

    # Pending count metric
    client.index(
        index='.kibana',
        id='visualization:pending-count',
        body={
            'type': 'visualization',
            'visualization': {
                'title': 'Pending Approvals Count',
                'visState': json.dumps({
                    'title': 'Pending Approvals',
                    'type': 'metric',
                    'params': {
                        'metric': {
                            'style': {'bgColor': '#ffc107', 'fontSize': 60}
                        }
                    },
                    'aggs': [{'id': '1', 'type': 'count', 'schema': 'metric'}]
                }),
                'kibanaSavedObjectMeta': {
                    'searchSourceJSON': json.dumps({
                        'index': 'job-events',
                        'query': {'term': {'status': 'PENDING_APPROVAL'}}
                    })
                }
            }
        }
    )
    print("Created visualization: Pending Count")

    # Approval form (markdown with iframe)
    client.index(
        index='.kibana',
        id='visualization:approval-form',
        body={
            'type': 'visualization',
            'visualization': {
                'title': 'Approval Form',
                'visState': json.dumps({
                    'title': 'Submit Approval Decision',
                    'type': 'markdown',
                    'params': {
                        'markdown': f'<iframe src="{api_endpoint}/approvals/embed-form" width="100%" height="450" frameborder="0" style="border: 1px solid #ddd; border-radius: 4px;"></iframe>'
                    }
                })
            }
        }
    )
    print("Created visualization: Approval Form")


def create_dashboard(client):
    """Create the approval dashboard."""
    client.index(
        index='.kibana',
        id='dashboard:approval-dashboard',
        body={
            'type': 'dashboard',
            'dashboard': {
                'title': 'Job Approval Dashboard',
                'description': 'Review and approve/reject jobs with quality failures',
                'panelsJSON': json.dumps([
                    {
                        'panelIndex': '1',
                        'gridData': {'x': 0, 'y': 0, 'w': 12, 'h': 8},
                        'panelRefName': 'panel_1',
                        'embeddableConfig': {}
                    },
                    {
                        'panelIndex': '2',
                        'gridData': {'x': 12, 'y': 0, 'w': 36, 'h': 8},
                        'panelRefName': 'panel_2',
                        'embeddableConfig': {}
                    },
                    {
                        'panelIndex': '3',
                        'gridData': {'x': 0, 'y': 8, 'w': 48, 'h': 15},
                        'panelRefName': 'panel_3',
                        'embeddableConfig': {}
                    }
                ]),
                'optionsJSON': json.dumps({
                    'hidePanelTitles': False,
                    'useMargins': True
                }),
                'timeRestore': True,
                'timeTo': 'now',
                'timeFrom': 'now-7d',
                'refreshInterval': {'pause': False, 'value': 30000}
            },
            'references': [
                {'name': 'panel_1', 'type': 'visualization', 'id': 'pending-count'},
                {'name': 'panel_2', 'type': 'search', 'id': 'pending-approvals'},
                {'name': 'panel_3', 'type': 'visualization', 'id': 'approval-form'}
            ]
        }
    )
    print("Created dashboard: Job Approval Dashboard")


def main():
    api_endpoint = os.environ.get('APPROVAL_API_ENDPOINT', 'https://your-api.execute-api.region.amazonaws.com')

    client = get_client()

    create_index_pattern(client)
    create_saved_searches(client)
    create_visualizations(client, api_endpoint)
    create_dashboard(client)

    print("\nDashboard setup complete!")
    print(f"Access at: https://{os.environ['OPENSEARCH_ENDPOINT']}/_dashboards")


if __name__ == '__main__':
    main()
```

## User Flow

1. **Job fails quality check** → Status set to `PENDING_APPROVAL` in OpenSearch

2. **User opens OpenSearch Dashboard** → Sees "Pending Approvals" count and list

3. **User reviews job details** → Clicks on job to see quality metrics, historical trends

4. **User submits decision** → Uses embedded form with:
   - Job Run ID (can click from pending list)
   - Decision (Approve/Reject)
   - Reason (required)
   - Name/Email

5. **Form submits to API** → Lambda:
   - Validates request
   - Updates OpenSearch document (immediate feedback)
   - Publishes to `job_approvals` SNS topic

6. **Dashboard updates** → Job moves from "Pending" to "Approved/Rejected"

7. **Downstream triggered** → `downstream_orchestrator` picks up approval event

## Summary

| Component | Purpose |
|-----------|---------|
| OpenSearch Dashboard | Visual interface for reviewing and approving jobs |
| Embedded Form | HTML form served by Lambda, embedded via iframe |
| Approval API Lambda | Handles form submissions, updates OpenSearch, publishes to SNS |
| API Gateway | HTTP endpoint for the approval API |
| SNS Topic | `job_approvals` - triggers downstream processing |

This solution requires minimal infrastructure beyond what's already deployed, provides a visual demo-friendly experience, and keeps all job data and approvals in one place.
