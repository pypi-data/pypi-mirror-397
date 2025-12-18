# Simple ETL Example

A minimal example demonstrating the SparkRouter pattern.

## Files

| File | Description |
|------|-------------|
| `simple_job.py` | The job class with business logic |
| `simple_job_factory.py` | Factory that creates jobs with dependencies |
| `test_simple_job.py` | Tests using Noop implementations |

## Pattern Overview

```
Entry Point (databricks/glue/container)
    ↓
main(**kwargs)
    ↓
SimpleETLJobFactory.run(**kwargs)
    ↓
SimpleETLJobFactory.create_job()  →  injects dependencies
    ↓
SimpleETLJob.run()  →  Template Method
    ↓
SimpleETLJob.execute_job()  →  Your business logic
    ↓
SimpleETLJob.on_success() or on_failure()
```

## Running the Example

### Local / Container

```bash
python -m sparkrouter.entry_points.container \
    --module_name examples.simple_etl.simple_job_factory \
    --simple_etl_job '{"notification": {"type": "noop"}}' \
    --input_path "s3://bucket/input/" \
    --output_path "s3://bucket/output/"
```

### Databricks

```python
# In Airflow DAG
task = DatabricksSubmitRunOperator(
    task_id='simple_etl',
    spark_python_task={
        'python_file': 'dbfs:/scripts/databricks/entry.py',
        'parameters': [
            '--module_name', 'mypackage.simple_etl.simple_job_factory',
            '--simple_etl_job', '{"notification": {"type": "noop"}}',
            '--input_path', 's3://bucket/input/',
            '--output_path', 's3://bucket/output/',
        ]
    }
)
```

### AWS Glue

```python
# In Airflow DAG
task = GlueJobOperator(
    task_id='simple_etl',
    job_name='simple_etl_job',
    script_location='s3://bucket/scripts/glue/entry.py',
    script_args={
        '--module_name': 'mypackage.simple_etl.simple_job_factory',
        '--simple_etl_job': '{"notification": {"type": "noop"}}',
        '--input_path': 's3://bucket/input/',
        '--output_path': 's3://bucket/output/',
    }
)
```

## Testing

Run the example tests:

```bash
pytest examples/simple_etl/test_simple_job.py -v
```

The tests use `NoopNotificationService` instead of mocks, allowing you to:
- Test real job behavior
- Assert notifications were triggered
- Verify notification content
