# Getting Job ID from Spark

## Summary

**Yes**, every Spark job has a unique identifier available.

### Universal Solution (All Platforms)

```python
job_run_id = spark.sparkContext.applicationId
```

This works on **all platforms** (Glue, Databricks, EMR, Container) and is stable for the entire job run. Perfect for correlating logs, metrics, and UI entries.

Example: `application_1234567890_0001` or `local-1234567890`

### Platform-Specific IDs (Optional)

If you need platform-native job/run IDs:

| Platform | Native ID Available? | Method |
|----------|---------------------|--------|
| AWS Glue | ✅ Yes | `spark.conf.get("JOB_RUN_ID")` |
| Databricks | ✅ Yes | `spark.conf.get("spark.databricks.job.runId")` |
| EMR | ⚠️ Use applicationId | `spark.sparkContext.applicationId` |
| Container/Local | ⚠️ Use applicationId | `spark.sparkContext.applicationId` |

---

## AWS Glue

Glue automatically passes `JOB_RUN_ID` as a command-line argument.

### Method 1: From Spark Config
```python
job_run_id = spark.conf.get("JOB_RUN_ID", "unknown")
```

### Method 2: From Command Line Args (Glue entry point)
```python
from awsglue.utils import getResolvedOptions
args = getResolvedOptions(sys.argv, ['JOB_RUN_ID'])
job_run_id = args['JOB_RUN_ID']
```

**Note**: Our Glue entry point (`scripts/glue/generic_entry.py`) currently **filters out** `JOB_RUN_ID` from kwargs to avoid passing it to job factories. We'd need to capture it before filtering.

---

## Databricks

### Method 1: From Spark Config (Recommended)
```python
job_id = spark.conf.get("spark.databricks.job.id", "unknown")
run_id = spark.conf.get("spark.databricks.job.runId", "unknown")
```

### Method 2: From dbutils Tags
```python
tags = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags()
job_id = tags.get("jobId").getOrElse("unknown")
run_id = tags.get("runId").getOrElse("unknown")
cluster_id = tags.get("clusterId").getOrElse("unknown")
```

### Available Tags
- `jobId` - Job definition ID
- `runId` - Unique run ID for this execution
- `clusterId` - Cluster where job is running
- `user` - User who triggered the job

---

## EMR

EMR doesn't have a "job run ID" concept like Glue, but you can use:

```python
# Spark application ID (unique per job run)
app_id = spark.sparkContext.applicationId  # e.g., "application_1234567890_0001"

# EMR cluster ID (from instance metadata)
import requests
cluster_id = requests.get(
    "http://169.254.169.254/latest/meta-data/instance-id",
    timeout=1
).text
```

---

## Container/Local

No platform-provided job ID. Options:

### Option 1: Spark Application ID
```python
app_id = spark.sparkContext.applicationId
```

### Option 2: Generate Your Own
```python
import uuid
job_run_id = str(uuid.uuid4())
```

---

## Recommendation: Simple Solution

For most use cases, just use `applicationId` directly:

```python
# In your job
job_run_id = spark.sparkContext.applicationId

metrics = {
    'job_name': 'transform_images',
    'job_run_id': job_run_id,  # Works on all platforms
    'extract': {...},
    'transform': {...},
    'load': {...}
}
```

This is:
- ✅ **Universal** - works on all platforms
- ✅ **Stable** - same ID for entire job run
- ✅ **No configuration needed** - always available
- ✅ **Useful** - correlates logs, metrics, UI entries

## Advanced: Context Service (Optional)

If you need platform-specific IDs or additional context:

```python
from typing import Optional
from pyspark.sql import SparkSession

class ExecutionContextService:
    """Get execution context from different platforms"""

    def __init__(self, spark: SparkSession, service_provider: str):
        self.spark = spark
        self.service_provider = service_provider

    def get_job_run_id(self) -> str:
        """Get universal job run ID (Spark application ID)"""
        return self.spark.sparkContext.applicationId

    def get_platform_run_id(self) -> Optional[str]:
        """Get platform-specific run ID (if available)"""
        if self.service_provider == 'GLUE':
            return self.spark.conf.get("JOB_RUN_ID", None)
        elif self.service_provider == 'DATABRICKS':
            return self.spark.conf.get("spark.databricks.job.runId", None)
        return None

    def get_platform_job_id(self) -> Optional[str]:
        """Get platform job definition ID (if available)"""
        if self.service_provider == 'GLUE':
            return self.spark.conf.get("JOB_ID", None)
        elif self.service_provider == 'DATABRICKS':
            return self.spark.conf.get("spark.databricks.job.id", None)
        return None

    def get_execution_context(self) -> dict:
        """Get complete execution context"""
        return {
            'job_run_id': self.get_job_run_id(),  # Universal
            'platform_run_id': self.get_platform_run_id(),  # Platform-specific
            'platform_job_id': self.get_platform_job_id(),  # Platform-specific
            'service_provider': self.service_provider,
        }
```

---

## Important Notes

1. **Glue entry point filters JOB_RUN_ID**: `scripts/glue/generic_entry.py` removes it from kwargs. Either:
   - Capture it in entry point and pass explicitly
   - Get it from Spark config in job instead

2. **Spark config is platform-specific**: Always provide fallback values

3. **Container/Local has no run ID**: Use Spark application ID or generate UUID

4. **Consistency**: Use `ExecutionContextService` to abstract platform differences
