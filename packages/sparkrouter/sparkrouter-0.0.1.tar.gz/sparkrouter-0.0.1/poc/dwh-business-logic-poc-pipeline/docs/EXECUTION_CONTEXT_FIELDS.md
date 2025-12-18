# Execution Context Fields - Job Metrics

## Overview

Job metrics now capture comprehensive execution context to enable filtering, comparison, and analysis across different job runs, platforms, and environments.

## New Fields Added

### Execution Context

| Field | Type | Description | Example | Source |
|-------|------|-------------|---------|--------|
| **`job_status`** | string | Job outcome | `SUCCESS`, `FAILED` | Set by job on completion |
| **`start_date`** | string | User-requested start date | `2024-01-01` | Job parameter |
| **`end_date`** | string | User-requested end date | `2024-01-31` | Job parameter |
| **`created_by`** | string | User/system that triggered job | `airflow`, `john.doe`, `manual` | Job parameter |
| **`service_provider`** | string | Execution platform | `GLUE`, `DATABRICKS`, `EMR`, `CONTAINER` | Entry point / kwargs |
| **`environment`** | string | Deployment environment | `sandbox`, `dev`, `prod` | Environment variable or kwargs |
| **`region`** | string | AWS region | `us-west-1`, `us-east-1` | Environment variable or kwargs |
| **`source_base_path`** | string | Data source location | `s3://bucket/raw/images` | Extractor config |
| **`sink_base_path`** | string | Data destination location | `s3://bucket/processed/images` | Loader config |

### Previously Added

| Field | Type | Description | Example | Source |
|-------|------|-------------|---------|--------|
| **`job_run_id`** | string | Spark application ID | `application_1234567890_0001` | `spark.sparkContext.applicationId` |

---

## How Fields Are Populated

### 1. Job Parameters (Captured in `execute_job()`)

```python
# transform_images_job.py execute_job()
metrics.start_date = start_date
metrics.end_date = end_date
metrics.created_by = created_by
```

These are passed by the caller (Airflow, manual invocation, etc.).

### 2. Platform Context (From `**kwargs`)

```python
# transform_images_job.py execute_job()
metrics.service_provider = kwargs.get('service_provider', None)
metrics.environment = kwargs.get('environment', None)
metrics.region = kwargs.get('region', None)
```

Set by entry points:
- **Glue**: `scripts/glue/generic_entry.py` sets `service_provider='GLUE'`, reads `environment` and `region` from env vars
- **Databricks**: Would set `service_provider='DATABRICKS'`
- **Container**: Would set `service_provider='CONTAINER'`

### 3. Data Paths (From Components)

```python
# transform_images_job.py execute_job()
metrics.source_base_path = self.extract.base_s3_path
metrics.sink_base_path = self.image_loader.base_s3_path
```

Extracted from extractor and loader components.

### 4. Job Outcome (Set on Completion)

```python
# transform_images_job.py execute_job()
metrics.job_status = "SUCCESS"  # On successful completion
```

Set to `"FAILED"` in error handling (future enhancement).

### 5. Spark Application ID (From Spark Context)

```python
# transform_images_job.py _capture_resource_metrics()
metrics.job_run_id = sc.applicationId
```

Universal across all Spark platforms.

---

## Environment Variables

### Glue Entry Point

The Glue entry point (`scripts/glue/generic_entry.py`) reads these environment variables:

```bash
ENVIRONMENT=sandbox   # Deployment environment (sandbox, dev, prod)
AWS_REGION=us-west-1  # AWS region (fallback: AWS_DEFAULT_REGION)
```

These are set automatically by AWS Glue when the job runs.

### Manual Override

You can pass these as command-line arguments to override defaults:

```bash
--environment prod
--region us-east-1
```

---

## Example Metrics JSON Output

```json
{
  "job_name": "TransformImagesJob",
  "job_run_id": "application_1234567890_0001",
  "job_status": "SUCCESS",
  "start_time": "2024-12-11T10:30:00Z",
  "end_time": "2024-12-11T10:35:23Z",
  "duration_seconds": 323.45,

  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "created_by": "airflow-dag-123",
  "service_provider": "GLUE",
  "environment": "sandbox",
  "region": "us-west-1",
  "source_base_path": "s3://sfly-aws-dwh-sandbox-jc-us-west-1-data/raw/images",
  "sink_base_path": "s3://sfly-aws-dwh-sandbox-jc-us-west-1-data/processed/images",

  "extract": {
    "records_read": 15000,
    "duration_seconds": 45.2
  },
  "transform": {
    "records_output": 14800,
    "duration_seconds": 180.1
  },
  "load": {
    "records_written": 14800,
    "files_written": 56,
    "duration_seconds": 98.15
  },
  "total_dropped": 200,
  "drop_reasons": {
    "decryption_failure": 150,
    "null_critical_fields": 50
  }
}
```

---

## OpenSearch Dashboard Queries

With these new fields, you can now create powerful filters and comparisons:

### Filter by Platform

```
service_provider: "GLUE"
```

### Filter by Environment

```
environment: "prod"
```

### Filter by Date Range Processed

```
start_date: "2024-01-01" AND end_date: "2024-01-31"
```

### Compare Performance Across Platforms

Create visualization:
- **Metrics**: Average `duration_seconds`
- **Buckets**: Terms on `service_provider`

### Track Who's Running Jobs

Create visualization:
- **Metrics**: Count
- **Buckets**: Terms on `created_by.keyword`

### Regional Performance Comparison

Create visualization:
- **Metrics**: Average `duration_seconds`
- **Buckets**: Date Histogram on `@timestamp`, Split by `region.keyword`

---

## Testing

### Unit/Functional Tests

Tests don't have access to real Spark context, so these fields will be `None`:
- `job_run_id` = None
- `service_provider` = None (unless explicitly set)
- `environment` = None (unless explicitly set)
- `region` = None (unless explicitly set)

This is expected and acceptable.

### Integration Tests

When running against real Glue:
- All fields should be populated
- Verify in OpenSearch dashboard

---

## Future Enhancements

Additional context that could be added:

1. **`code_version`** - Track deployments and correlate performance changes
2. **`glue_job_name`** - Actual Glue job name (different from "TransformImagesJob")
3. **`cluster_id`** - For long-running clusters (Databricks, EMR)
4. **`triggered_by`** - Scheduled vs manual vs event-driven
5. **`git_commit_sha`** - Exact code version running
6. **`airflow_dag_id`** - If triggered by Airflow
7. **`airflow_task_id`** - Specific Airflow task

---

## Summary

**Before**: Job metrics only tracked processing statistics (records, duration, drops)

**After**: Job metrics now include:
- ✅ **Who** ran it (`created_by`)
- ✅ **Where** it ran (`service_provider`, `environment`, `region`)
- ✅ **What data** it processed (`start_date`, `end_date`, `source_base_path`, `sink_base_path`)
- ✅ **How** it performed (`job_status`, `job_run_id`, all the processing metrics)

This enables comprehensive analysis, filtering, and comparison for management dashboards.
