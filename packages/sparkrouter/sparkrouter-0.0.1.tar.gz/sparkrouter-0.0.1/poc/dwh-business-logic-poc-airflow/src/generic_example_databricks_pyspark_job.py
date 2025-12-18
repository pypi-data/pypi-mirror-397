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


DAG_ID = 'generic-example-databricks-job'

LOGIC_MODULE = 'dwh.jobs.generic_example.generic_example_job_factory'
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

INSTANCE_PROFILE = Variable.get('DATABRICKS_INSTANCE_PROFILE', f'arn:aws:iam::{ACCOUNT_ID}:instance-profile/sfly-aws-dwh-{ENV}-svc-consumer-databricks-worker-InstanceProfile')
if INSTANCE_PROFILE == 'None':
    raise ValueError("DATABRICKS_INSTANCE_PROFILE is not set. Please set it in Airflow Variables.")

with DAG(
    dag_id=DAG_ID,
    default_args={},
    schedule=None,
    catchup=False,
    description="Generic example Databricks job DAG",
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
            "ENV": f"{ENV}"
        },
        "aws_attributes": {
            "instance_profile_arn": INSTANCE_PROFILE
        }
    }

    job_args = {
        '--module_name': LOGIC_MODULE,
        '--generic_example_job': json.dumps({
            'alarm_service': ALARM_SERVICE

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
                "python_file": f"{S3_CODE_PATH}/scripts/{ENTRYPOINT}",
                "parameters": parameters,
            },
            "libraries": [
                {"whl": f"{S3_CODE_PATH}/dwh_pipeline_poc-{CODE_VERSION}-py3-none-any.whl"},
            ],
            # allows users in consumer-developers group to see the job run details in Databricks UI
            "access_control_list": [{
                "group_name": "consumer-developers",
                "permission_level": "CAN_VIEW"
            }],
            "init_scripts": [{
                "s3": {
                    "destination": f"{S3_CODE_PATH}/scripts/databricks_init.sh",
                    "region": "us-east-1"
                }
            }],
        },
        retries=0,
        retry_delay=timedelta(minutes=5),
        do_xcom_push=True,
    )
