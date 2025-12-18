import json
from datetime import timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import GlueJobSensor
from airflow.models import Variable, Param
from airflow.utils.types import NOTSET


DAG_ID = 'load-promos-glue-pyspark-job'

LOGIC_MODULE = 'dwh.jobs.load_promos.load_promos_job_factory'
ENTRYPOINT = "glue/generic_entry.py"

ENV = 'sandbox'
S3_REGION = 'us-west-1'
CODE_BUCKET = 'sfly-aws-dwh-sandbox-jc-mwaa-us-west-1-code'
CODE_PREFIX = 'code'
CODE_VERSION = '0.3.0'
S3_CODE_PATH = f's3://{CODE_BUCKET}/{CODE_PREFIX}/{CODE_VERSION}'

GLUE_REGION = 'us-west-1'
GLUE_ROLE_NAME = 'sfly-aws-dwh-sandbox-jc-mwaa-glue'

ALERTS_SNS_TOPIC = "arn:aws:sns:us-west-1:542605267262:dwh-pipeline-alerts-jc"
DATA_QUALITY_SNS_TOPIC = "arn:aws:sns:us-west-1:542605267262:dwh-pipeline-quality-jc"
GLUE_CONNECTION_NAME = 'sfly-aws-dwh-sandbox-jc-mwaa-postgres-connection'

DATA_BUCKET = 'sfly-aws-dwh-sandbox-jc-mwaa-us-west-1-data'
S3_DATA_SOURCE = Variable.get('S3_DATA_SOURCE', f's3://{DATA_BUCKET}/source')
S3_DATA_SINK_UNITY = Variable.get('S3_DATA_SINK_UNITY', f's3://{DATA_BUCKET}/unity')
S3_DATA_SINK_STAGE = Variable.get('S3_DATA_SINK_STAGE', f's3://{DATA_BUCKET}/stage')

dag = DAG(
    DAG_ID,
    default_args={},
    dagrun_timeout=timedelta(hours=10),
    schedule=None,
    catchup=False,
    params={
        'start_date': Param(default=NOTSET, type="string", description="Start date for the job, in ISO format (YYYY-MM-DD)"),
        'end_date': Param(default=NOTSET, type="string", description="End date for the job, in ISO format (YYYY-MM-DD)"),
        'created_by': Param(default='jclark', type="string", description="User who created the job")
    })


run_glue_job = GlueJobOperator(
    task_id='glue_job',
    job_name=f"{DAG_ID}_{CODE_VERSION}",
    script_location=f"{S3_CODE_PATH}/scripts/glue/generic_entry.py",
    script_args={
        '--module_name': LOGIC_MODULE,
        '--load_promos_job': json.dumps({
            "job_failed_notifications": {"notification_service": "SNS", "topic_arn": ALERTS_SNS_TOPIC, "region": GLUE_REGION},
            "job_success_notifications": {"notification_service": "SNS", "topic_arn": ALERTS_SNS_TOPIC, "region": GLUE_REGION},
            "data_quality_notifications": {"notification_service": "SNS", "topic_arn": DATA_QUALITY_SNS_TOPIC, "region": GLUE_REGION},
            "schema_service": {
                "ddl_reader": "S3",
                "region": S3_REGION,
                "bucket": CODE_BUCKET,
                "prefix": f"{CODE_PREFIX}/{CODE_VERSION}",
            },
            "extractor_config": {"strategy": "PARQUET", "source_table": S3_DATA_SOURCE},
            "unity_loader_config": {"strategy": "DELTA", "path": S3_DATA_SINK_UNITY},
            "stage_loader_config": {"strategy": "PARQUET", "path": S3_DATA_SINK_STAGE},
            "redshift_loader_config": {
                "strategy": "POSTGRES",
                "jdbc_url": "jdbc:postgresql://sfly-aws-dwh-sandbox-jc-mwaa-postgres.cqofdzmexbzb.us-west-1.rds.amazonaws.com:5432/jc",
                "properties": {
                    "user": "postgres",
                    "password": "Postgres1234!",
                    "driver": "org.postgresql.Driver",
                    'glue_connection': GLUE_CONNECTION_NAME
                }
            }
        }),
        '--start_date': "{{ params.start_date }}",
        '--end_date': "{{ params.end_date }}",
        '--created_by': "{{ params.created_by }}",
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
            '--python-modules-installer-option': '-r',
            '--additional-python-modules': f"{S3_CODE_PATH}/requirements.txt",
            '--connections': GLUE_CONNECTION_NAME,
        },
        "Tags": {
            "Environment": ENV.capitalize(),
            "App": "poc",
            "DataClassification": "AllDatasets",
            "ManagedBy": "DataPlatformOperations",
            "BusinessUnit": "Consumer",
            "Provisioner": "Terraform",
            "Project": "DWH-POC",
            "Owner": "jclark",
        }
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
