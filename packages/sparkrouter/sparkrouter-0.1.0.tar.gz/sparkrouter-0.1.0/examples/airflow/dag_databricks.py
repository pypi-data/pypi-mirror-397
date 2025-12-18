"""
Airflow DAG Example - Databricks
================================

Example DAG for running SparkRouter jobs on Databricks via MWAA.

This demonstrates:
- Using DatabricksSubmitRunOperator to run SparkRouter jobs
- Passing JSON configuration via parameters
- Using existing Databricks clusters or job clusters
- Chaining multiple jobs in a pipeline
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.databricks.operators.databricks import (
    DatabricksSubmitRunOperator,
)

# Default arguments for all tasks
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Shared cluster configuration for job clusters
NEW_CLUSTER_CONFIG = {
    "spark_version": "13.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 2,
    "aws_attributes": {
        "instance_profile_arn": "arn:aws:iam::123456789:instance-profile/databricks-role",
    },
}

# DAG definition
with DAG(
    dag_id="sparkrouter_databricks_example",
    default_args=default_args,
    description="SparkRouter ETL pipeline on Databricks",
    schedule_interval="0 6 * * *",  # Daily at 6 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sparkrouter", "databricks", "etl"],
) as dag:

    # Task 1: Extract and transform data (using job cluster)
    transform_task = DatabricksSubmitRunOperator(
        task_id="transform_data",
        databricks_conn_id="databricks_default",
        new_cluster=NEW_CLUSTER_CONFIG,
        spark_python_task={
            "python_file": "dbfs:/scripts/databricks/entry.py",
            "parameters": [
                "--module_name", "mypackage.jobs.transform.transform_job_factory",
                "--transform_job", """{
                    "notification": {
                        "type": "sns",
                        "topic_arn": "arn:aws:sns:us-east-1:123456789:job-alerts"
                    }
                }""",
                "--input_path", "s3://my-bucket/raw/{{ ds }}/",
                "--output_path", "s3://my-bucket/transformed/{{ ds }}/",
                "--partition_date", "{{ ds }}",
            ],
        },
        libraries=[
            {"pypi": {"package": "sparkrouter"}},
            {"pypi": {"package": "mypackage"}},
        ],
    )

    # Task 2: Load to Delta table (using existing cluster)
    load_task = DatabricksSubmitRunOperator(
        task_id="load_to_delta",
        databricks_conn_id="databricks_default",
        existing_cluster_id="1234-567890-abcdef",  # Existing interactive cluster
        spark_python_task={
            "python_file": "dbfs:/scripts/databricks/entry.py",
            "parameters": [
                "--module_name", "mypackage.jobs.load.load_job_factory",
                "--load_job", """{
                    "source": {
                        "type": "parquet",
                        "path": "s3://my-bucket/transformed/{{ ds }}/"
                    },
                    "destination": {
                        "type": "delta",
                        "catalog": "main",
                        "schema": "analytics",
                        "table": "fact_events",
                        "mode": "merge",
                        "merge_keys": ["id"]
                    },
                    "notification": {
                        "type": "sns",
                        "topic_arn": "arn:aws:sns:us-east-1:123456789:job-alerts"
                    }
                }""",
                "--partition_date", "{{ ds }}",
            ],
        },
    )

    # Task 3: Data quality check (lightweight, small cluster)
    quality_task = DatabricksSubmitRunOperator(
        task_id="data_quality_check",
        databricks_conn_id="databricks_default",
        new_cluster={
            **NEW_CLUSTER_CONFIG,
            "num_workers": 1,  # Smaller cluster for quality checks
        },
        spark_python_task={
            "python_file": "dbfs:/scripts/databricks/entry.py",
            "parameters": [
                "--module_name", "mypackage.jobs.quality.quality_check_job_factory",
                "--quality_check_job", """{
                    "checks": [
                        {"type": "row_count", "min": 1000},
                        {"type": "null_check", "columns": ["id", "timestamp"]},
                        {"type": "freshness", "column": "timestamp", "max_age_hours": 24}
                    ],
                    "notification": {
                        "type": "sns",
                        "topic_arn": "arn:aws:sns:us-east-1:123456789:job-alerts"
                    }
                }""",
                "--catalog", "main",
                "--schema", "analytics",
                "--table", "fact_events",
                "--partition_date", "{{ ds }}",
            ],
        },
    )

    # Define task dependencies
    transform_task >> load_task >> quality_task


# Alternative: Using DatabricksRunNowOperator for pre-defined jobs
# This is useful when you have Databricks Jobs already configured in the UI
#
# from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
#
# run_existing_job = DatabricksRunNowOperator(
#     task_id="run_existing_job",
#     databricks_conn_id="databricks_default",
#     job_id=12345,  # Pre-configured Databricks Job ID
#     notebook_params={
#         "module_name": "mypackage.jobs.transform.transform_job_factory",
#         "partition_date": "{{ ds }}",
#     },
# )
