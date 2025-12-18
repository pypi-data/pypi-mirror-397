"""
Filter Images Glue DAG

This DAG runs the filter_images Glue job, triggered by the event_dispatcher
when transform_images completes successfully.

Parameters received from event_dispatcher:
    - transform_output_path: S3 path to transform_images output
    - start_date: Start date of the transform job
    - end_date: End date of the transform job
    - created_by: User who triggered the transform job
    - triggered_by_job: Name of triggering job (transform_images)
    - triggered_by_run_id: Run ID of triggering job

The job is cumulative throughout the day - it reads previous filtered
output and combines with new transform output, deduplicating with
"last duplicate wins" strategy.
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.models import Variable
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.operators.python import PythonOperator
import json

# Glue job configuration from Airflow Variables
GLUE_JOB_NAME = Variable.get("filter_images_glue_job_name", default_var="filter-images-job")
GLUE_IAM_ROLE = Variable.get("glue_iam_role", default_var="")
AWS_REGION = Variable.get("aws_region", default_var="us-west-1")

# Filter images job configuration
FILTER_BASE_PATH = Variable.get(
    "filter_images_base_path",
    default_var="s3://dwh-data/filtered_images"
)
FILTER_TIMEZONE = Variable.get(
    "filter_images_timezone",
    default_var="America/Los_Angeles"
)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}


def log_parameters(**context):
    """Log the parameters received from the dispatcher."""
    conf = context['dag_run'].conf or {}

    print("=" * 60)
    print("FILTER IMAGES - DAG RUN CONFIGURATION")
    print("=" * 60)
    print(f"Run ID: {context['dag_run'].run_id}")
    print(f"Triggered by job: {conf.get('triggered_by_job', 'N/A')}")
    print(f"Triggered by run: {conf.get('triggered_by_run_id', 'N/A')}")
    print("-" * 60)
    print("Parameters:")
    print(f"  transform_output_path: {conf.get('transform_output_path', 'N/A')}")
    print(f"  start_date: {conf.get('start_date', 'N/A')}")
    print(f"  end_date: {conf.get('end_date', 'N/A')}")
    print(f"  created_by: {conf.get('created_by', 'N/A')}")
    print("-" * 60)
    print(f"Full conf: {conf}")
    print("=" * 60)

    # Validate required parameters
    if not conf.get('transform_output_path'):
        raise ValueError("transform_output_path is required but was not provided")

    return conf


def build_glue_job_arguments(**context) -> dict:
    """
    Build arguments for the Glue job.

    Constructs the filter_images_job configuration JSON from DAG parameters.
    """
    conf = context['dag_run'].conf or {}

    # Build the job configuration
    filter_images_job_config = {
        "base_path": FILTER_BASE_PATH,
        "timezone": FILTER_TIMEZONE,
        "transform_output_path": conf.get('transform_output_path'),
        "triggered_by_job": conf.get('triggered_by_job', 'transform_images'),
        "triggered_by_run_id": conf.get('triggered_by_run_id', 'unknown'),
        "dedup_key_columns": ["mediaid"],
        "dedup_order_column": "updated",
        "time_column": "updated",
        "event_publisher_config": {
            "publisher_type": "SNS"
        }
    }

    # Build Glue job arguments
    glue_args = {
        '--module_name': 'dwh.jobs.filter_images.filter_images_job_factory',
        '--filter_images_job': json.dumps(filter_images_job_config),
        '--has_spark': 'true',
        '--service_provider': 'GLUE',
        '--start_date': conf.get('start_date', ''),
        '--end_date': conf.get('end_date', ''),
        '--created_by': conf.get('created_by', 'airflow'),
    }

    print(f"Glue job arguments: {json.dumps(glue_args, indent=2)}")

    # Push to XCom for the GlueJobOperator
    context['ti'].xcom_push(key='glue_job_arguments', value=glue_args)

    return glue_args


dag = DAG(
    'filter_images_glue',
    default_args=default_args,
    description='Run filter_images Glue job - cumulative filtering with manifest tracking',
    schedule_interval=None,  # Triggered by event_dispatcher
    catchup=False,
    tags=['glue', 'filter', 'etl'],
)

# Task 1: Log parameters
log_params = PythonOperator(
    task_id='log_parameters',
    python_callable=log_parameters,
    dag=dag,
)

# Task 2: Build Glue job arguments
build_args = PythonOperator(
    task_id='build_glue_job_arguments',
    python_callable=build_glue_job_arguments,
    dag=dag,
)

# Task 3: Run Glue job
run_glue_job = GlueJobOperator(
    task_id='run_filter_images_glue',
    job_name=GLUE_JOB_NAME,
    script_args="{{ ti.xcom_pull(task_ids='build_glue_job_arguments', key='glue_job_arguments') }}",
    region_name=AWS_REGION,
    iam_role_name=GLUE_IAM_ROLE,
    dag=dag,
    # Wait for job to complete
    wait_for_completion=True,
    # Check status every 60 seconds
    check_job_status_wait_time=60,
    # Verbose logging
    verbose=True,
)

log_params >> build_args >> run_glue_job
