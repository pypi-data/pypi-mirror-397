# Event Publishing Design

> **Note**: This document describes the current implemented architecture. The alerts topic
> and AlertEvaluator/AlertSender components described in earlier versions were not implemented
> and have been removed from this document. Human alerting is currently handled through
> the existing notification services.

## Problem Statement

The current design has three notification topics:
1. **Job Success** - downstream processing + metrics
2. **Job Failed** - human alert
3. **Data Quality** - quality reporting (red = also triggers failure)

### Two Types of Job Failures

**1. Catastrophic Failure (Exception)**
- Processing was interrupted
- No data was loaded
- Artifacts may be incomplete or missing
- Requires: Fix code or fix source data, then re-run
- Downstream: Cannot proceed

**2. Quality Failure**
- Processing completed successfully
- Data was loaded to target location
- Quality check ran post-load and failed
- Artifacts exist and are complete
- Requires: Human decision - either fix source data and re-run, OR accept the data and continue
- Downstream: Blocked pending human approval

This distinction is critical: quality failures have usable artifacts waiting for approval, while catastrophic failures do not.

### Issues with Current Design

1. **Conflates alerting with event publishing**
   - Success ≠ "No Alert Needed" (job can succeed but warrant attention)
   - Failure ≠ "No Downstream Processing" (quality failures have complete artifacts)

2. **Quality failures create notification cascade**
   - Quality check fails → publishes to quality topic (red)
   - Job fails due to quality → publishes to failure topic
   - Two notifications for the same root cause

3. **No workflow for quality approval**
   - Quality failures produce artifacts that need human review
   - No mechanism to "approve" and trigger downstream processing
   - No mechanism to "reject" and trigger re-processing

4. **Tight coupling**
   - Job decides who gets notified based on success/failure
   - Adding new consumers requires changing job code

## Proposed Design

### Job Outcome States

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Job Execution                              │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   Exception during      │
                    │   processing?           │
                    └─────────────────────────┘
                         │              │
                        YES             NO
                         │              │
                         ▼              ▼
              ┌──────────────┐   ┌─────────────────┐
              │ CATASTROPHIC │   │  Data loaded    │
              │   FAILURE    │   │  successfully   │
              │              │   └─────────────────┘
              │ • No data    │            │
              │ • No artifacts│           ▼
              │ • Fix & rerun│   ┌─────────────────┐
              └──────────────┘   │ Quality check   │
                                 └─────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                  GREEN            YELLOW              RED
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌───────────┐    ┌────────────┐    ┌─────────────┐
             │  SUCCESS  │    │  SUCCESS   │    │  PENDING    │
             │           │    │  (warning) │    │  APPROVAL   │
             │ • Auto    │    │ • Auto     │    │             │
             │   proceed │    │   proceed  │    │ • Artifacts │
             │           │    │ • Alert    │    │   exist     │
             └───────────┘    └────────────┘    │ • Human     │
                                               │   decides   │
                                               └─────────────┘
                                                     │
                                        ┌────────────┴────────────┐
                                        │                         │
                                     APPROVE                   REJECT
                                        │                         │
                                        ▼                         ▼
                                 ┌────────────┐           ┌────────────┐
                                 │  APPROVED  │           │  REJECTED  │
                                 │            │           │            │
                                 │ • Proceed  │           │ • Fix data │
                                 │   downstream│          │ • Re-run   │
                                 └────────────┘           └────────────┘
```

### Topic 1: `job_events` (always published, machine consumers)

Every job run publishes one event with complete context:

```json
{
    "event_type": "job_completed",
    "job_name": "transform_images",
    "job_run_id": "abc123",
    "timestamp": "2024-01-15T10:30:00Z",

    "status": "SUCCESS | PENDING_APPROVAL | FAILED",
    "failure_type": null | "CATASTROPHIC" | "QUALITY",

    "artifacts_available": true | false,
    "artifacts": {
        "nautilus": {"path": "s3://bucket/nautilus/transformed_images", "records": 50000, "bytes": 600000},
        "savedproject": {"path": "s3://bucket/savedproject/transformed_images", "records": 48000, "bytes": 634567}
    },

    "quality": {
        "status": "GREEN | YELLOW | RED",
        "checks": [
            {"name": "drop_rate", "status": "GREEN", "value": 0.02, "threshold": 0.05},
            {"name": "null_rate", "status": "YELLOW", "value": 0.08, "threshold": 0.10},
            {"name": "schema_match", "status": "GREEN", "value": true}
        ]
    },

    "metrics": {
        "records_read": 100000,
        "records_written": 98000,
        "records_dropped": 2000,
        "bytes_written": 1234567,
        "duration_seconds": 120
    },

    "error": null | {
        "type": "ValueError",
        "message": "...",
        "stack_trace": "..."
    }
}
```

**Status Values:**
- `SUCCESS` - Quality GREEN or YELLOW, downstream can auto-proceed
- `PENDING_APPROVAL` - Quality RED, artifacts exist, awaiting human decision
- `FAILED` - Catastrophic failure, no usable artifacts

**Consumers:**
- Downstream processors: filter `status == "SUCCESS"`, read artifacts
- Approval workflow: filter `status == "PENDING_APPROVAL"`, wait for approval event
- Dashboards/monitoring: aggregate all events
- Retry systems: filter `status == "FAILED"` (catastrophic only)

### Topic 2: `job_approvals` (human decisions on quality failures)

When a human reviews a `PENDING_APPROVAL` job:

```json
{
    "event_type": "approval_decision",
    "job_name": "transform_images",
    "job_run_id": "abc123",
    "timestamp": "2024-01-15T11:00:00Z",

    "decision": "APPROVED | REJECTED",
    "decided_by": "jsmith@company.com",
    "reason": "Drop rate elevated due to known bad batch from vendor, acceptable for this run"
}
```

**On APPROVED:** Downstream processors can now consume the artifacts
**On REJECTED:** Artifacts should be cleaned up, source data fixed, job re-run

## Implementation

### Core Components

```python
class JobEventPublisher:
    """Publishes to job_events topic - always called."""

    def publish(self, job_name: str, metrics: dict, quality: QualityResult, error: Exception = None):
        event = {
            "event_type": "job_completed",
            "job_name": job_name,
            "job_run_id": metrics.get("job_run_id"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "status": "FAILED" if error or quality.status == "RED" else "SUCCESS",
            "failure_reason": self._determine_failure_reason(error, quality),
            "quality": quality.to_dict(),
            "metrics": metrics,
            "artifacts": metrics.get("artifacts", {})
        }
        self._send("job_events", event)
        return event

    def _determine_failure_reason(self, error: Exception, quality: QualityResult) -> str | None:
        if error and not isinstance(error, QualityCheckFailedError):
            return "EXCEPTION"
        if quality.status == "RED":
            return "QUALITY_RED"
        return None
```

### Job Integration

```python
class TransformImagesJob(AbstractJob):
    def __init__(
        self,
        event_publisher: JobEventPublisher,
        quality_checker: QualityChecker,
        ...
    ):
        self.event_publisher = event_publisher
        self.quality_checker = quality_checker

    def execute_job(self, ...):
        # ... run ETL phases ...

        # Run quality checks
        quality_result = self.quality_checker.check(metrics)

        # Fail job if quality is RED
        if quality_result.status == "RED":
            raise QualityCheckFailedError(quality_result)

        return metrics

    def run(self, **kwargs):
        error = None
        metrics = {}
        quality = QualityResult(status="GREEN", checks=[])

        try:
            metrics = self.execute_job(**kwargs)
            quality = self.quality_checker.check(metrics)
            if quality.status == "RED":
                raise QualityCheckFailedError(quality)
        except Exception as e:
            error = e

        # Always publish event to job_events topic
        self.event_publisher.publish(
            job_name="transform_images",
            metrics=metrics,
            quality=quality,
            error=error
        )

        if error:
            raise error
```

### Quality Checker

```python
@dataclass
class QualityCheck:
    name: str
    status: str  # GREEN, YELLOW, RED
    value: any
    threshold: any = None
    message: str = None


@dataclass
class QualityResult:
    status: str  # GREEN, YELLOW, RED (worst of all checks)
    checks: list[QualityCheck]

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "checks": [
                {"name": c.name, "status": c.status, "value": c.value, "threshold": c.threshold}
                for c in self.checks
            ]
        }


class QualityChecker:
    """Job-specific quality checks."""

    def __init__(self, config: dict):
        self.drop_rate_yellow = config.get("drop_rate_yellow", 0.05)
        self.drop_rate_red = config.get("drop_rate_red", 0.10)
        self.min_records = config.get("min_records", 0)

    def check(self, metrics: dict) -> QualityResult:
        checks = []

        # Drop rate check
        records_read = metrics.get("records_read", 0)
        records_dropped = metrics.get("records_dropped", 0)
        drop_rate = records_dropped / records_read if records_read > 0 else 0

        if drop_rate >= self.drop_rate_red:
            checks.append(QualityCheck("drop_rate", "RED", drop_rate, self.drop_rate_red))
        elif drop_rate >= self.drop_rate_yellow:
            checks.append(QualityCheck("drop_rate", "YELLOW", drop_rate, self.drop_rate_yellow))
        else:
            checks.append(QualityCheck("drop_rate", "GREEN", drop_rate, self.drop_rate_yellow))

        # Minimum records check
        records_written = metrics.get("records_written", 0)
        if records_written < self.min_records:
            checks.append(QualityCheck("min_records", "RED", records_written, self.min_records))
        else:
            checks.append(QualityCheck("min_records", "GREEN", records_written, self.min_records))

        # Determine overall status (worst of all checks)
        overall = "GREEN"
        if any(c.status == "YELLOW" for c in checks):
            overall = "YELLOW"
        if any(c.status == "RED" for c in checks):
            overall = "RED"

        return QualityResult(status=overall, checks=checks)
```

## Summary

| Topic | When Published | Consumers | Purpose |
|-------|---------------|-----------|---------|
| `job_events` | Always | Downstream processors, dashboards, analytics | Complete record of every job run |
| `job_approvals` | Human decision on quality failure | Downstream processors, workflow systems | Unblock or reject PENDING_APPROVAL jobs |

## Current Implementation Status

**Implemented:**
- `job_events` topic with SNS publishing
- `job_approvals` topic for human decisions
- `job_events_indexer` Lambda - indexes all events to OpenSearch
- `approval_processor` Lambda - updates OpenSearch with approval decisions
- `downstream_orchestrator` Lambda - triggers next jobs on SUCCESS/APPROVED

**Not Implemented (Future):**
- Automated alert evaluation and routing (PagerDuty, Slack)
- Threshold-based quality checking with configurable rules
- Approval workflow UI (API, CLI, dashboard forms)

## Open Questions

- [ ] What quality checks are needed per job type?
- [ ] What are the appropriate thresholds for yellow/red?
- [ ] Should anomaly detection compare against historical data?
- [ ] How to handle alert fatigue (rate limiting, deduplication)?
- [ ] Where should alert rules be configured (code vs external config)?
