import json

from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import GlueJobSensor
from airflow.models import Variable, Param
from airflow.utils.types import NOTSET


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


DAG_ID = 'generic-example-glue-pyspark-job'

LOGIC_MODULE = 'dwh.jobs.generic_example.generic_example_job_factory'
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


dag = DAG(
    DAG_ID,
    default_args={},
    schedule=None,
    catchup=False,
    description="Generic example Glue PyShell job DAG",
    params={
        'start_date': Param(default=NOTSET, type="string", description="Start date for the job, in ISO format (YYYY-MM-DD)"),
        'end_date': Param(default=NOTSET, type="string", description="End date for the job, in ISO format (YYYY-MM-DD)"),
    })

run_glue_job = GlueJobOperator(
    task_id='glue_job',
    job_name=f"{DAG_ID}_{CODE_VERSION}",
    script_location=f"{S3_CODE_PATH}/scripts/{ENTRYPOINT}",
    script_args={
        '--module_name': LOGIC_MODULE,
        '--generic_example_job': json.dumps({
            'alarm_service': ALARM_SERVICE,
        }),
        '--start_date': "{{ params.start_date }}",
        '--end_date': "{{ params.end_date }}",
    },
    s3_bucket=CODE_BUCKET,
    iam_role_name=GLUE_ROLE_NAME,
    run_job_kwargs={
        'Timeout': 5
    },
    create_job_kwargs={
        'GlueVersion': '5.0',
        'NumberOfWorkers': 2,
        'WorkerType': 'G.1X',
        'DefaultArguments': {
            '--enable-metrics': 'true',
            '--enable-continuous-cloudwatch-log': 'true',
            '--extra-py-files': f"{S3_CODE_PATH}/dwh_pipeline_poc-{CODE_VERSION}-py3-none-any.whl",
            # tellme: this is awkward, but pyshell jobs don't support requirements.txt
            # todo: perhaps we can add this logic to entry_point.py instead? That would make much more sense
            # tellme: solution needs to work for both pyshell and pyscript jobs
            # https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-python-libraries.html
            '--python-modules-installer-option': '-r',
            '--additional-python-modules': f"{S3_CODE_PATH}/requirements.txt",
        },
        # TELLME: WAITING FOR IAM ROLE TO BE UPDATED
        # "Tags": {
        #     "Environment": ENV.capitalize(),
        #     "App": "poc",
        #     "DataClassification": "AllDatasets",
        #     "ManagedBy": "DataPlatformOperations",
        #     "BusinessUnit": "Consumer",
        #     "Provisioner": "Terraform",
        #     "Project": "DWH-POC",
        #     "Owner": "jclark",
        # }
    },
    dag=dag
)

# Optional: Add a sensor to wait for job completion
wait_for_glue_job = GlueJobSensor(
    task_id='wait_for_glue_job',
    job_name=f"{DAG_ID}_{CODE_VERSION}",
    run_id="{{ task_instance.xcom_pull(task_ids='glue_job', key='return_value') }}",
    dag=dag
)

run_glue_job >> wait_for_glue_job
