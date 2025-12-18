# Event Handling Architecture

This document describes the downstream processing architecture for job events and approvals. It supplements [ALERTING.md](ALERTING.md) which covers the event publishing design.

> **Note**: This document has been updated to reflect the current implementation.
> The alerts topic and associated routing were not implemented and have been removed.

## Current Implementation

### SNS Topics (Infrastructure)
```
dwh-{env}-job-events      → Lambda subscriptions (indexer, orchestrator)
dwh-{env}-job-approvals   → Lambda subscriptions (processor, orchestrator)
```

### Lambda Functions
- `job_events_indexer.py` - Indexes all job events to OpenSearch
- `approval_processor.py` - Updates OpenSearch with approval decisions
- `downstream_orchestrator.py` - Triggers next jobs on SUCCESS/APPROVED

## Architecture

### Topic to Handler Mapping

| Topic | Handler | Purpose |
|-------|---------|---------|
| `job_events` | Lambda: `job_events_indexer` | Index ALL events to OpenSearch for dashboards |
| `job_events` | Lambda: `downstream_orchestrator` | Trigger next jobs on SUCCESS |
| `job_approvals` | Lambda: `approval_processor` | Update OpenSearch, trigger downstream on APPROVED |

### Handler Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                        job_events topic                              │
│                                                                      │
│  Published by: Jobs (always, on completion)                          │
│  Contains: status, quality, metrics, artifacts, error                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
         ┌──────────────────┐        ┌──────────────────┐
         │ job_events_      │        │ downstream_      │
         │ indexer          │        │ orchestrator     │
         │                  │        │                  │
         │ • Index ALL      │        │ • Filter:        │
         │   events to      │        │   status=SUCCESS │
         │   OpenSearch     │        │ • Trigger next   │
         │ • Common index   │        │   job/workflow   │
         │ • Job index      │        │                  │
         └──────────────────┘        └──────────────────┘


┌─────────────────────────────────────────────────────────────────────┐
│                      job_approvals topic                             │
│                                                                      │
│  Published by: Human (via UI/API after reviewing PENDING_APPROVAL)   │
│  Contains: decision (APPROVED/REJECTED), decided_by, reason          │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
                    ▼                           ▼
         ┌──────────────────┐        ┌──────────────────┐
         │ approval_        │        │ downstream_      │
         │ processor        │        │ orchestrator     │
         │                  │        │                  │
         │ • Update job     │        │ • Filter:        │
         │   event in       │        │   decision=      │
         │   OpenSearch     │        │   APPROVED       │
         │ • Record who     │        │ • Trigger next   │
         │   decided & why  │        │   job/workflow   │
         └──────────────────┘        └──────────────────┘
```

## Lambda Specifications

### 1. job_events_indexer

**Purpose:** Index all job events to OpenSearch for dashboards and analytics.

**Trigger:** SNS subscription to `job_events` topic

**Input Schema:** (from ALERTING.md)
```json
{
    "event_type": "job_completed",
    "job_name": "transform_images",
    "job_run_id": "abc123",
    "timestamp": "2024-01-15T10:30:00Z",
    "status": "SUCCESS | PENDING_APPROVAL | FAILED",
    "failure_type": null | "CATASTROPHIC" | "QUALITY",
    "artifacts_available": true,
    "artifacts": {...},
    "quality": {"status": "GREEN|YELLOW|RED", "checks": [...]},
    "metrics": {...},
    "error": null | {...}
}
```

**OpenSearch Indexes:**
- `job-events` - Common index for cross-job dashboards
- `job-events-{job_name}` - Job-specific index for deep-dive analysis

**Document Structure:**
```json
{
    "id": "generated-hash",
    "timestamp": "2024-01-15T10:30:00Z",
    "event_type": "job_completed",

    "job_name": "transform_images",
    "job_run_id": "abc123",
    "status": "SUCCESS",
    "failure_type": null,

    "quality_status": "GREEN",
    "quality_checks": [...],

    "artifacts_available": true,
    "artifacts": {...},

    "records_read": 100000,
    "records_written": 98000,
    "records_dropped": 2000,
    "bytes_written": 1234567,
    "duration_seconds": 120,

    "extract_duration_seconds": 30,
    "transform_duration_seconds": 60,
    "load_duration_seconds": 30,

    "approval_status": null,
    "approved_by": null,
    "approval_reason": null,
    "approval_timestamp": null
}
```

**Key Changes from Current `job_metrics_processor`:**
1. Rename `job_status` → `status` (align with new schema)
2. Add `failure_type` field
3. Add `quality_status` and `quality_checks` fields
4. Add `artifacts_available` and `artifacts` fields
5. Add approval tracking fields (populated by approval_processor)
6. Change index names: `job-metrics` → `job-events`

### 2. approval_processor

**Purpose:** Process human approval decisions and update job event records.

**Trigger:** SNS subscription to `job_approvals` topic

**Input Schema:**
```json
{
    "event_type": "approval_decision",
    "job_name": "transform_images",
    "job_run_id": "abc123",
    "timestamp": "2024-01-15T11:00:00Z",
    "decision": "APPROVED | REJECTED",
    "decided_by": "jsmith@company.com",
    "reason": "Drop rate elevated due to known bad batch, acceptable"
}
```

**Actions:**
1. Find original job event in OpenSearch by `job_run_id`
2. Update document with approval fields:
   ```json
   {
       "approval_status": "APPROVED",
       "approved_by": "jsmith@company.com",
       "approval_reason": "Drop rate elevated due to known bad batch, acceptable",
       "approval_timestamp": "2024-01-15T11:00:00Z"
   }
   ```
3. Index approval event separately for audit trail

**OpenSearch Indexes:**
- Updates existing document in `job-events` and `job-events-{job_name}`
- Creates new document in `job-approvals` for audit trail

### 3. downstream_orchestrator

**Purpose:** Trigger downstream jobs/workflows when data is ready.

**Triggers:**
- SNS subscription to `job_events` (filter: `status = SUCCESS`)
- SNS subscription to `job_approvals` (filter: `decision = APPROVED`)

**Actions:**
1. Look up workflow configuration for the job
2. Determine next step(s) in the pipeline
3. Trigger next job(s) via:
   - AWS Step Functions
   - Glue Workflow
   - Direct Glue Job start
   - EventBridge event

**Configuration Example:**
```json
{
    "transform_images": {
        "on_success": [
            {"type": "glue_job", "job_name": "load_to_redshift"},
            {"type": "step_function", "arn": "arn:aws:states:..."}
        ]
    }
}
```

**Note:** This lambda is optional for POC. Manual triggering or Airflow/Step Functions may handle orchestration instead.

## SNS Subscription Filters

### For downstream_orchestrator on job_events

```json
{
    "status": ["SUCCESS"]
}
```

Only triggers when job completes successfully (GREEN or YELLOW quality).

### For downstream_orchestrator on job_approvals

```json
{
    "decision": ["APPROVED"]
}
```

Only triggers when human approves a quality failure.

## Implementation Options

### Option A: Separate Lambdas (Recommended for Production)

```
lambda/
├── job_events_indexer.py      # Indexes to OpenSearch
├── approval_processor.py       # Handles approval decisions
└── downstream_orchestrator.py  # Triggers next workflows
```

**Pros:**
- Clear separation of concerns
- Independent scaling
- Easier debugging and monitoring
- Can have different memory/timeout settings

**Cons:**
- More Lambda functions to manage
- Slightly higher cold start potential

### Option B: Single Lambda with Multiple Handlers (Simpler for POC)

```
lambda/
└── event_processor.py
    ├── job_events_handler()
    ├── approval_handler()
    └── orchestration_handler()
```

**Terraform Configuration:**
```hcl
resource "aws_lambda_function" "job_events_indexer" {
  function_name = "job-events-indexer"
  handler       = "event_processor.job_events_handler"
  # ...
}

resource "aws_lambda_function" "approval_processor" {
  function_name = "approval-processor"
  handler       = "event_processor.approval_handler"
  # ...
}
```

**Pros:**
- Single codebase
- Shared utilities
- Easier deployment

**Cons:**
- All handlers share same memory/timeout
- Larger deployment package

### Option C: Minimal POC (Start Here)

For initial POC, start with just:

1. **Refactor `job_metrics_processor.py` → `job_events_indexer.py`**
   - Update to handle new event schema
   - Index all events (SUCCESS, PENDING_APPROVAL, FAILED)

2. **Skip `approval_processor` initially**
   - Manual OpenSearch updates for approvals
   - Add when approval workflow is built

3. **Skip `downstream_orchestrator` initially**
   - Use Airflow or manual triggering
   - Add when automated pipelines are needed

## Infrastructure Changes

### SNS Topics (infra module)

```hcl
resource "aws_sns_topic" "job_events" {
  name = "dwh-${var.environment}-job-events"
}

resource "aws_sns_topic" "job_approvals" {
  name = "dwh-${var.environment}-job-approvals"
}
```

### Lambda Subscriptions

```hcl
# job_events_indexer subscribes to job_events (all events)
resource "aws_sns_topic_subscription" "job_events_to_indexer" {
  topic_arn = aws_sns_topic.job_events.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.job_events_indexer.arn
}

# approval_processor subscribes to job_approvals
resource "aws_sns_topic_subscription" "approvals_to_processor" {
  topic_arn = aws_sns_topic.job_approvals.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.approval_processor.arn
}

# downstream_orchestrator subscribes to job_events (SUCCESS only)
resource "aws_sns_topic_subscription" "job_events_to_orchestrator" {
  topic_arn = aws_sns_topic.job_events.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.downstream_orchestrator.arn
  filter_policy = jsonencode({
    status = ["SUCCESS"]
  })
}

# downstream_orchestrator subscribes to job_approvals (APPROVED only)
resource "aws_sns_topic_subscription" "approvals_to_orchestrator" {
  topic_arn = aws_sns_topic.job_approvals.arn
  protocol  = "lambda"
  endpoint  = aws_lambda_function.downstream_orchestrator.arn
  filter_policy = jsonencode({
    decision = ["APPROVED"]
  })
}
```

## OpenSearch Index Mappings

### job-events index

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
            "quality_checks": {"type": "nested"},

            "artifacts_available": {"type": "boolean"},
            "artifacts": {"type": "object"},

            "records_read": {"type": "long"},
            "records_written": {"type": "long"},
            "records_dropped": {"type": "long"},
            "bytes_written": {"type": "long"},
            "duration_seconds": {"type": "float"},

            "approval_status": {"type": "keyword"},
            "approved_by": {"type": "keyword"},
            "approval_reason": {"type": "text"},
            "approval_timestamp": {"type": "date"},

            "error_type": {"type": "keyword"},
            "error_message": {"type": "text"}
        }
    }
}
```

### job-approvals index (audit trail)

```json
{
    "mappings": {
        "properties": {
            "timestamp": {"type": "date"},
            "event_type": {"type": "keyword"},

            "job_name": {"type": "keyword"},
            "job_run_id": {"type": "keyword"},

            "decision": {"type": "keyword"},
            "decided_by": {"type": "keyword"},
            "reason": {"type": "text"},

            "original_quality_status": {"type": "keyword"},
            "original_quality_checks": {"type": "nested"}
        }
    }
}
```

## Open Questions

- [ ] Should `downstream_orchestrator` be a Lambda or Step Functions?
- [ ] How should workflow configuration be stored (DynamoDB, SSM Parameter Store, code)?
- [ ] Should approvals have an expiration (auto-reject after N days)?
- [ ] Do we need a dead-letter queue for failed Lambda invocations?
- [ ] Should we add CloudWatch alarms for Lambda errors?
