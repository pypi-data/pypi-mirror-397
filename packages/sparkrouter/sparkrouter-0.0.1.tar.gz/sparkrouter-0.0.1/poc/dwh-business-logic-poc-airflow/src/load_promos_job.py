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


DAG_ID = 'load-promos-databricks-job'

LOGIC_MODULE = 'dwh.jobs.load_promos.load_promos_job_factory'
ENTRYPOINT = "databricks/generic_entry.py"
CODE_VERSION = '0.3.0'

ENV = Variable.get('ENV', 'dev')
ACCOUNT_ID = get_account_id(ENV)

CODE_BUCKET = Variable.get('CODE_BUCKET', f'sfly-aws-dwh-{ENV}-consumer-databricks-scripts')
CODE_PREFIX = Variable.get('CODE_PREFIX', 'code')
S3_CODE_PATH = f's3://{CODE_BUCKET}/{CODE_PREFIX}/{CODE_VERSION}'

JOB_FAILED_NOTIFICATION_SERVICE = json.loads(Variable.get('JOB_FAILED_NOTIFICATION_SERVICE', json.dumps({
    "notification_service": "NOOP"
})))
JOB_SUCCESS_NOTIFICATION_SERVICE = json.loads(Variable.get('JOB_SUCCESS_NOTIFICATION_SERVICE', json.dumps({
    "notification_service": "NOOP"
})))
JOB_DQ_NOTIFICATION_SERVICE = json.loads(Variable.get('JOB_DQ_NOTIFICATION_SERVICE', json.dumps({
    "notification_service": "NOOP"
})))
S3_SOURCE_PATH = Variable.get('S3_SOURCE_PATH', 's3a://test-data/source/promotions/')
S3_STAGING_PATH = Variable.get('S3_STAGING_PATH', 's3a://test-data/staging/promotions/')

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
            'job_failed_notifications': JOB_FAILED_NOTIFICATION_SERVICE,
            'job_success_notifications': JOB_SUCCESS_NOTIFICATION_SERVICE,
            'data_quality_notifications': JOB_DQ_NOTIFICATION_SERVICE,
            "extractor_config": {
                "strategy": "PARQUET",
                "source_table": S3_SOURCE_PATH,
            },
            "stage_loader_config": {
                "strategy": "PARQUET",
                "source_table": S3_STAGING_PATH,
            },
            "unity_loader_config": {
                "strategy": "DELTA",
                "path": "s3a://test-data/unity-catalog/promotions/d_promotion_3_0/"
            },
            "redshift_loader_config": {
                "strategy": "POSTGRES",
                "jdbc_url": "jdbc:postgresql://postgres:5432/postgres_db",
                "properties": {
                    "user": "postgres_user",
                    "password": "postgres_password",
                    "driver": "org.postgresql.Driver"
                }
            }
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
