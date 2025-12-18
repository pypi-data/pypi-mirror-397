"""
Documentation:
This DAG is used to create and run an AWS Glue PyShell job.
A race condition was discovered in the GlueJobOperator/GlueJobHook
where the internal configuration for the job payload (notably the "MaxCapacity" parameter)
isn't fully built unless the hook's create_glue_job_config() method is explicitly invoked prior to job creation.

Workaround:
- We create a custom GluePyShellJobCreator which uses boto3 to create the job directly.
"""
import json
from datetime import timedelta
from airflow import DAG
from airflow.providers.amazon.aws.sensors.glue import GlueJobSensor
from airflow.operators.python import PythonOperator
from airflow.models import Variable, Param
from airflow.utils.types import NOTSET

from operators.glue_pyshell_job_creator import GluePyShellJobCreator


def get_account_id(env):
    if env == 'prod' or env == 'qa':
        return '157816743405'
    elif env == 'sandbox':
        return '542605267262'
    elif env == 'dev':
        return '530191758819'
    else:
        raise ValueError(f"get_account_id: Unknown environment: {env}")


def get_region(env):
    if env == 'prod' or env == 'qa' or env == 'dev':
        return 'us-east-1'
    elif env == 'sandbox':
        return 'us-west-1'
    else:
        raise ValueError(f"get_region: Unknown environment: {env}")


DAG_ID = 'sql-example-glue-pyshell-job'

LOGIC_MODULE = 'dwh.jobs.sql_example.sql_example_job_factory'
ENTRYPOINT = "glue/generic_entry.py"
CODE_VERSION = '0.2.0'

ENV = Variable.get('ENV', 'dev')
ACCOUNT_ID = get_account_id(ENV)
REGION = get_region(ENV)

CODE_BUCKET = Variable.get('CODE_BUCKET', f'sfly-aws-dwh-{ENV}-consumer-databricks-scripts')
CODE_PREFIX = Variable.get('CODE_PREFIX', 'code')
S3_CODE_PATH = f's3://{CODE_BUCKET}/{CODE_PREFIX}/{CODE_VERSION}'

GLUE_REGION = Variable.get('GLUE_REGION', REGION)
# Use only the role name (not ARN) for GlueJobOperator
GLUE_ROLE_NAME = Variable.get('GLUE_ROLE_NAME', f'sfly-aws-dwh-{ENV}-svc-glue-service')

ALARM_SERVICE = json.loads(Variable.get('ALARM_SERVICE_TYPE', json.dumps({
    "notification_service": "NOOP"
})))
EMAIL_SERVICE = json.loads(Variable.get('EMAIL_SERVICE_TYPE', json.dumps({
    "service_type": "NOOP"
})))

GLUE_CONNECTION_NAME = Variable.get('REDSHIFT_GLUE_CONNECTION', "glue-redshift-connection-test")
REDSHIFT_CONNECTION = json.loads(Variable.get('REDSHIFT_GLUE_CONNECTION', json.dumps({
    "database_type": "REDSHIFT",
    "credentials_provider": {
        "provider_type": "GLUE_CONNECTION",
        "region": GLUE_REGION,
        "glue_connection_name": GLUE_CONNECTION_NAME
    },
    "force_direct_connection": "False"
})))

dag = DAG(
    DAG_ID,
    default_args={},
    dagrun_timeout=timedelta(hours=10),
    schedule=None,
    catchup=False,
    params={
        'start_date': Param(default=NOTSET, type="string", description="Start date for the job, in ISO format (YYYY-MM-DD)"),
        'end_date': Param(default=NOTSET, type="string", description="End date for the job, in ISO format (YYYY-MM-DD)"),
    })


# Define a function to create and run the Glue job using our custom class
def create_and_run_glue_job(**kwargs):
    ti = kwargs['ti']
    params = kwargs['params']

    start_date = params.get('start_date')
    end_date = params.get('end_date')

    # Format job name and script location
    job_name = f"{DAG_ID}_{CODE_VERSION}"
    script_location = f"{S3_CODE_PATH}/scripts/{ENTRYPOINT}"

    # Create default arguments
    default_arguments = {
        '--job-language': 'python',
        '--enable-metrics': 'true',
        '--enable-continuous-cloudwatch-log': 'true',
        '--extra-py-files': f"{S3_CODE_PATH}/dwh_pipeline_poc-{CODE_VERSION}-py3-none-any.whl",
        # tellme: this is awkward, but pyshell jobs don't support requirements.txt
        # todo: perhaps we can add this logic to entry_point.py instead? That would make much more sense
        # tellme: solution needs to work for both pyshell and pyscript jobs
        '--additional-python-modules': 'pandas>=1.5.0,psycopg2-binary==2.9.10,pymongo>=4.0.0,redis>=4.0.0',
        '--connections': GLUE_CONNECTION_NAME,
    }

    # Job runtime arguments
    job_args = {
        '--module_name': LOGIC_MODULE,
        '--sql_example_job': json.dumps({
            'alarm_service': ALARM_SERVICE,
            'email_service': EMAIL_SERVICE,
            'postgres_connection': REDSHIFT_CONNECTION,
        }),
        '--start_date': start_date,
        '--end_date': end_date,
    }

    # Create the job creator
    job_creator = GluePyShellJobCreator(
        job_name=job_name,
        role_name=GLUE_ROLE_NAME,
        script_location=script_location,
        default_arguments=default_arguments,
        # TELLME: WAITING FOR IAM ROLE TO BE UPDATED
        # tags={
        #     "App": "poc",
        #     "BusinessUnit": "Consumer",
        #     "DataClassification": "AllDatasets",
        #     "Environment": "Sandbox",
        #     "ManagedBy": "DataPlatformOperations",
        #     "Owner": "jclark",
        #     "Project": "DWH-POC",
        #     "Provisioner": "Terraform"
        # },
        region_name=GLUE_REGION,
        timeout=5
    )

    # Create the job if it doesn't exist and run it
    job_run_id = job_creator.run_job(job_args)

    # Push the job run ID to XCom for the sensor to use
    ti.xcom_push(key='return_value', value=job_run_id)
    return job_run_id


# Replace the GlueJobOperator with our custom PythonOperator
run_glue_job = PythonOperator(
    task_id='glue_job',
    python_callable=create_and_run_glue_job,
    provide_context=True,
    dag=dag
)

# Keep the sensor as is - it will work with our job run ID
wait_for_glue_job = GlueJobSensor(
    task_id='wait_for_glue_job',
    job_name=f"{DAG_ID}_{CODE_VERSION}",
    run_id="{{ task_instance.xcom_pull(task_ids='glue_job', key='return_value') }}",
    dag=dag
)

run_glue_job >> wait_for_glue_job
