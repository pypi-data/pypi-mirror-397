"""
Airflow DAG Example - AWS Glue
==============================

Example DAG for running SparkRouter jobs on AWS Glue via MWAA.

This demonstrates:
- Using GlueJobOperator to run SparkRouter jobs
- Passing JSON configuration via script_args
- Chaining multiple jobs in a pipeline
"""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

# Default arguments for all tasks
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# DAG definition
with DAG(
    dag_id="sparkrouter_glue_example",
    default_args=default_args,
    description="SparkRouter ETL pipeline on AWS Glue",
    schedule_interval="0 6 * * *",  # Daily at 6 AM UTC
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sparkrouter", "glue", "etl"],
) as dag:

    # Task 1: Extract and transform data
    transform_task = GlueJobOperator(
        task_id="transform_data",
        job_name="sparkrouter-transform-job",  # Pre-created Glue job name
        region_name="us-east-1",
        script_location="s3://my-bucket/scripts/glue/entry.py",
        script_args={
            "--module_name": "mypackage.jobs.transform.transform_job_factory",
            "--transform_job": """{
                "notification": {
                    "type": "sns",
                    "topic_arn": "arn:aws:sns:us-east-1:123456789:job-alerts"
                }
            }""",
            "--input_path": "s3://my-bucket/raw/{{ ds }}/",
            "--output_path": "s3://my-bucket/transformed/{{ ds }}/",
            "--partition_date": "{{ ds }}",
        },
        # Glue job configuration
        num_of_dpus=10,
        iam_role_name="GlueETLRole",
    )

    # Task 2: Load to data warehouse
    load_task = GlueJobOperator(
        task_id="load_to_warehouse",
        job_name="sparkrouter-load-job",
        region_name="us-east-1",
        script_location="s3://my-bucket/scripts/glue/entry.py",
        script_args={
            "--module_name": "mypackage.jobs.load.load_job_factory",
            "--load_job": """{
                "source": {
                    "type": "parquet",
                    "path": "s3://my-bucket/transformed/{{ ds }}/"
                },
                "destination": {
                    "type": "redshift",
                    "table": "analytics.fact_events",
                    "mode": "append"
                },
                "notification": {
                    "type": "sns",
                    "topic_arn": "arn:aws:sns:us-east-1:123456789:job-alerts"
                }
            }""",
            "--partition_date": "{{ ds }}",
        },
        num_of_dpus=5,
        iam_role_name="GlueETLRole",
    )

    # Task 3: Data quality check
    quality_task = GlueJobOperator(
        task_id="data_quality_check",
        job_name="sparkrouter-quality-job",
        region_name="us-east-1",
        script_location="s3://my-bucket/scripts/glue/entry.py",
        script_args={
            "--module_name": "mypackage.jobs.quality.quality_check_job_factory",
            "--quality_check_job": """{
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
            "--table": "analytics.fact_events",
            "--partition_date": "{{ ds }}",
        },
        num_of_dpus=2,
        iam_role_name="GlueETLRole",
    )

    # Define task dependencies
    transform_task >> load_task >> quality_task
