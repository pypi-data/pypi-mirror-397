# SparkRouter

[![PyPI version](https://badge.fury.io/py/sparkrouter.svg)](https://badge.fury.io/py/sparkrouter)
[![Python](https://img.shields.io/pypi/pyversions/sparkrouter.svg)](https://pypi.org/project/sparkrouter/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Platform-agnostic job routing framework for Spark ETL pipelines.**

Write your ETL logic once, run it on Databricks, AWS Glue, EMR, or Docker containers.

## Why SparkRouter?

- **Write Once, Run Anywhere**: Same job code runs on multiple Spark platforms
- **Clean Architecture**: Factory + Template Method patterns keep code testable
- **No Mocks Needed**: Dependency injection with Noop implementations for testing
- **Configuration-Driven**: JSON config via CLI, no code changes between environments

## Installation

```bash
uv add sparkrouter
# or
pip install sparkrouter
```

With optional dependencies:

```bash
uv add sparkrouter[spark]  # Include PySpark
uv add sparkrouter[aws]    # Include boto3
uv add sparkrouter[all]    # Include everything
```

## Quick Start

### 1. Define Your Job

```python
from sparkrouter import AbstractJob, AbstractJobFactory, NotificationService

class MyETLJob(AbstractJob):
    """Your ETL job with business logic."""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def execute_job(self, input_path: str, output_path: str) -> dict:
        # Your business logic here
        print(f"Processing {input_path} -> {output_path}")
        return {"records_processed": 1000}

    def on_success(self, results):
        self.notification_service.send_notification(
            subject="Job Success",
            message=f"Processed {results['records_processed']} records"
        )

    def on_failure(self, error_message):
        self.notification_service.send_notification(
            subject="Job Failed",
            message=error_message
        )
```

### 2. Create a Factory

```python
from sparkrouter.testing.noop import NoopNotificationService

class MyETLJobFactory(AbstractJobFactory):
    """Factory that assembles jobs with dependencies."""

    def create_job(self, **kwargs) -> MyETLJob:
        config = self.parse_job_config(job_name='my_etl_job', **kwargs)
        return MyETLJob(
            notification_service=NoopNotificationService()
        )

def main(**kwargs):
    """Entry point called by platform scripts."""
    factory = MyETLJobFactory()
    return factory.run(**kwargs)
```

### 3. Run It

```bash
# Local / Container
python -m sparkrouter.entry_points.container \
    --module_name mypackage.my_etl_job_factory \
    --my_etl_job '{}' \
    --input_path "s3://bucket/input/" \
    --output_path "s3://bucket/output/"
```

The same job runs on Databricks, Glue, or EMR - just use a different entry point.

## Architecture

```
Entry Point (platform-specific)
     │
     ▼
importlib.import_module(module_name).main(**kwargs)
     │
     ▼
AbstractJobFactory.run()
     │
     ▼
ConcreteFactory.create_job()  →  inject dependencies
     │
     ▼
AbstractJob.run()  →  Template Method (final)
     │
     ▼
ConcreteJob.execute_job()  →  Your business logic
     │
     ▼
on_success() or on_failure()
```

## Platform Entry Points

SparkRouter provides entry points for each platform:

| Platform | Entry Point | Service Provider |
|----------|-------------|------------------|
| Databricks | `sparkrouter.entry_points.databricks` | `DATABRICKS` |
| AWS Glue | `sparkrouter.entry_points.glue` | `GLUE` |
| Amazon EMR | `sparkrouter.entry_points.emr` | `EMR` |
| Container/Local | `sparkrouter.entry_points.container` | `CONTAINER` |

Each entry point:
1. Parses CLI arguments
2. Adds platform context (`service_provider`, `has_spark`)
3. Dynamically imports your module
4. Calls `main(**kwargs)`

## Airflow Integration

### AWS Glue

```python
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

task = GlueJobOperator(
    task_id='my_etl',
    job_name='my-glue-job',
    script_location='s3://bucket/scripts/glue/entry.py',
    script_args={
        '--module_name': 'mypackage.my_etl_job_factory',
        '--my_etl_job': '{"key": "value"}',
        '--input_path': 's3://bucket/input/',
        '--output_path': 's3://bucket/output/',
    },
)
```

### Databricks

```python
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

task = DatabricksSubmitRunOperator(
    task_id='my_etl',
    databricks_conn_id='databricks_default',
    spark_python_task={
        'python_file': 'dbfs:/scripts/databricks/entry.py',
        'parameters': [
            '--module_name', 'mypackage.my_etl_job_factory',
            '--my_etl_job', '{"key": "value"}',
            '--input_path', 's3://bucket/input/',
            '--output_path', 's3://bucket/output/',
        ],
    },
)
```

## Testing Without Mocks

SparkRouter encourages testing with Noop implementations instead of mocks:

```python
from sparkrouter.testing.noop import NoopNotificationService

def test_my_job():
    notifier = NoopNotificationService()
    job = MyETLJob(notification_service=notifier)

    result = job.run(input_path="/in", output_path="/out")

    assert result["records_processed"] == 1000
    assert len(notifier.notifications) == 1
    assert "Success" in notifier.notifications[0]["subject"]
```

## Examples

See the [examples](examples/) directory for complete working examples:

- [Simple ETL Job](examples/simple_etl/) - Basic job with factory pattern
- [Airflow DAGs](examples/airflow/) - Glue and Databricks DAG examples

## License

Apache License 2.0
