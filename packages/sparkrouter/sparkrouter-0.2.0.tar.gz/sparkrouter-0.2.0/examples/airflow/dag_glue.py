"""
Airflow DAG Example - AWS Glue

Minimal example showing how to run a SparkRouter job on AWS Glue.
"""

from datetime import datetime
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator

with DAG(
    dag_id="sparkrouter_glue_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    run_job = GlueJobOperator(
        task_id="run_etl_job",
        job_name="my-glue-job",
        # Entry script - see README.md#aws-glue for setup
        script_location="s3://my-bucket/scripts/glue_entry.py",
        script_args={
            # Points to your job factory module with main()
            "--module_name": "mypackage.jobs.my_job_factory",
            # These are passed to your execute_job() method
            "--input_path": "s3://my-bucket/input/",
            "--output_path": "s3://my-bucket/output/",
        },
    )
