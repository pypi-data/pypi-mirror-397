"""
Airflow DAG Example - Databricks

Minimal example showing how to run a SparkRouter job on Databricks.
"""

from datetime import datetime
from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator

with DAG(
    dag_id="sparkrouter_databricks_example",
    start_date=datetime(2024, 1, 1),
    schedule_interval=None,
    catchup=False,
) as dag:

    run_job = DatabricksSubmitRunOperator(
        task_id="run_etl_job",
        databricks_conn_id="databricks_default",
        new_cluster={
            "spark_version": "14.3.x-scala2.12",
            "node_type_id": "i3.xlarge",
            "num_workers": 2,
        },
        spark_python_task={
            # Entry script - see README.md#databricks for setup
            "python_file": "dbfs:/scripts/databricks_entry.py",
            "parameters": [
                # Points to your job factory module with main()
                "--module_name", "mypackage.jobs.my_job_factory",
                # These are passed to your execute_job() method
                "--input_path", "s3://my-bucket/input/",
                "--output_path", "s3://my-bucket/output/",
            ],
        },
        # Install sparkrouter and your job package
        libraries=[
            {"pypi": {"package": "sparkrouter"}},
            {"pypi": {"package": "mypackage"}},
        ],
    )
