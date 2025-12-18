import json
from datetime import timedelta
from airflow import DAG
from airflow.models import Param, Variable
from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
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


DAG_ID = 'sql-example-databricks-job'

LOGIC_MODULE = 'dwh.jobs.sql_example.sql_example_job_factory'
ENTRYPOINT = "databricks/generic_entry.py"
CODE_VERSION = '0.2.0'

ENV = Variable.get('ENV', 'dev')
ACCOUNT_ID = get_account_id(ENV)

CODE_BUCKET = Variable.get('CODE_BUCKET', f'sfly-aws-dwh-{ENV}-consumer-databricks-scripts')
CODE_PREFIX = Variable.get('CODE_PREFIX', 'code')
S3_CODE_PATH = f's3://{CODE_BUCKET}/{CODE_PREFIX}/{CODE_VERSION}'

ALARM_SERVICE = json.loads(Variable.get('ALARM_SERVICE_TYPE', json.dumps({
    "notification_service": "NOOP"
})))
EMAIL_SERVICE = json.loads(Variable.get('EMAIL_SERVICE_TYPE', json.dumps({
    "service_type": "NOOP"
})))
POSTGRES_CONNECTION = json.loads(Variable.get('POSTGRES_CONNECTION', json.dumps({
    "database_type": "POSTGRES",
    "credentials_provider": {
        "provider_type": "DIRECT",
        "connection_params": {
            "host": "postgres",
            "port": "5432",
            "database": "postgres_db",
            "user": "postgres_user",
            "password": "postgres_password"
        }
    },
    "force_direct_connection": "False"
})))

# INSTANCE_PROFILE = Variable.get('DATABRICKS_INSTANCE_PROFILE')
INSTANCE_PROFILE = Variable.get('DATABRICKS_INSTANCE_PROFILE', f'arn:aws:iam::{ACCOUNT_ID}:instance-profile/sfly-aws-dwh-{ENV}-svc-consumer-databricks-worker-InstanceProfile')
if INSTANCE_PROFILE == 'None':
    raise ValueError("DATABRICKS_INSTANCE_PROFILE is not set. Please set it in Airflow Variables.")

with DAG(
    dag_id=DAG_ID,
    default_args={},
    schedule=None,
    catchup=False,
    description="Sql example Databricks job DAG",
    params={
        'start_date': Param(default=NOTSET, type="string", description="Start date for the job, in ISO format (YYYY-MM-DD)"),
        'end_date': Param(default=NOTSET, type="string", description="End date for the job, in ISO format (YYYY-MM-DD)"),
    }
) as dag:

    cluster_config = {
        "spark_version": "15.4.x-scala2.12",
        "node_type_id": "mgd-fleet.xlarge",
        "driver_node_type_id": "mgd-fleet.xlarge",
        "num_workers": 1,
        "spark_env_vars": {
            "PYSPARK_PYTHON": "/databricks/python3/bin/python3",
            "ENV": "dev"
        },
        "aws_attributes": {
            "instance_profile_arn": INSTANCE_PROFILE
        }
    }

    job_args = {
        '--module_name': LOGIC_MODULE,
        '--sql_example_job': json.dumps({
            'alarm_service': ALARM_SERVICE,
            'email_service': EMAIL_SERVICE,
            'postgres_connection': POSTGRES_CONNECTION,
        }),
        '--start_date': "{{ params.start_date }}",
        '--end_date': "{{ params.end_date }}",
    }

    # Convert job_args dictionary to a flat list of alternating keys and values
    parameters = [item for k, v in job_args.items() for item in [k, v]]

    databricks_task = DatabricksSubmitRunOperator(
        task_id='generic-example-databricks-job',
        databricks_conn_id="databricks_consumer",
        json={
            "run_name": "test_databricks",
            "new_cluster": cluster_config,
            "timeout_seconds": 600,
            "spark_python_task": {
                "python_file": f"{S3_CODE_PATH}/scripts/databricks/generic_entry.py",
                "parameters": parameters
            },
            "libraries": [
                {"whl": f"{S3_CODE_PATH}/dwh_pipeline_poc-{CODE_VERSION}-py3-none-any.whl"},
                {"pypi": {"package": "arrow==1.2.1"}}
            ],
            # allows users in consumer-developers group to see the job run details in Databricks UI
            "access_control_list": [{
                "group_name": "consumer-developers",
                "permission_level": "CAN_VIEW"
            }]
        },
        retries=0,
        retry_delay=timedelta(minutes=5),
        do_xcom_push=True,
    )
