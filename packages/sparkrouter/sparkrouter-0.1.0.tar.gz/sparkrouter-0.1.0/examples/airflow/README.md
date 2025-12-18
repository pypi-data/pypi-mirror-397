# Airflow DAG Examples

Example DAGs for running SparkRouter jobs on AWS Glue and Databricks via MWAA or any Airflow deployment.

## Files

| File | Description |
|------|-------------|
| `dag_glue.py` | AWS Glue pipeline using GlueJobOperator |
| `dag_databricks.py` | Databricks pipeline using DatabricksSubmitRunOperator |

## Key Concepts

### Same Job, Different Platforms

The same SparkRouter job module runs on both platforms - only the entry point differs:

```
Glue:       s3://bucket/scripts/glue/entry.py
Databricks: dbfs:/scripts/databricks/entry.py
```

Both call the same job factory:
```
--module_name mypackage.jobs.transform.transform_job_factory
```

### Configuration via JSON

Job configuration is passed as a JSON string:

```python
"--transform_job", '{"notification": {"type": "sns", "topic_arn": "..."}}'
```

The factory's `parse_job_config()` handles parsing.

### Airflow Templating

Use Jinja templating for dynamic values:

```python
"--partition_date", "{{ ds }}",
"--input_path", "s3://bucket/raw/{{ ds }}/",
```

## AWS Glue Setup

### 1. Create Glue Job

```bash
aws glue create-job \
    --name sparkrouter-transform-job \
    --role GlueETLRole \
    --command '{"Name": "glueetl", "ScriptLocation": "s3://bucket/scripts/glue/entry.py"}' \
    --default-arguments '{"--extra-py-files": "s3://bucket/packages/mypackage.zip"}'
```

### 2. Upload Entry Point

Copy the SparkRouter Glue entry point to S3:

```bash
aws s3 cp sparkrouter/entry_points/glue.py s3://bucket/scripts/glue/entry.py
```

### 3. Package Your Jobs

```bash
cd mypackage
zip -r mypackage.zip mypackage/
aws s3 cp mypackage.zip s3://bucket/packages/
```

## Databricks Setup

### 1. Upload Entry Point to DBFS

```bash
databricks fs cp sparkrouter/entry_points/databricks.py dbfs:/scripts/databricks/entry.py
```

### 2. Install SparkRouter on Cluster

Either via cluster libraries or in the DAG:

```python
libraries=[
    {"pypi": {"package": "sparkrouter"}},
    {"pypi": {"package": "mypackage"}},
]
```

### 3. Configure Airflow Connection

```bash
airflow connections add databricks_default \
    --conn-type databricks \
    --conn-host https://your-workspace.cloud.databricks.com \
    --conn-password dapi_your_token
```

## Required Airflow Providers

```bash
# For AWS Glue
pip install apache-airflow-providers-amazon

# For Databricks
pip install apache-airflow-providers-databricks
```

## Pattern Summary

```
Airflow DAG
    ↓
GlueJobOperator / DatabricksSubmitRunOperator
    ↓
Platform Entry Point (glue.py / databricks.py)
    ↓
importlib.import_module(module_name).main(**kwargs)
    ↓
YourJobFactory.run(**kwargs)
    ↓
YourJob.execute_job(**filtered_kwargs)
```
