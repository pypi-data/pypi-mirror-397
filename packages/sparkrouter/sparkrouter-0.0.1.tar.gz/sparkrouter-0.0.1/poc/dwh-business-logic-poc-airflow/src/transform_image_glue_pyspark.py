import json
from datetime import timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import GlueJobSensor
from airflow.models import Variable, Param
from airflow.utils.types import NOTSET

DAG_ID = 'transform-image-glue-pyspark-job'

LOGIC_MODULE = 'dwh.jobs.transform_images.transform_images_job_factory'
ENTRYPOINT = "glue/generic_entry.py"

ENV = 'sandbox'
S3_REGION = 'us-west-1'
CODE_BUCKET = 'sfly-aws-dwh-sandbox-jc-code-us-west-1'
CODE_PREFIX = 'code'
CODE_VERSION = '0.3.0'
S3_CODE_PATH = f's3://{CODE_BUCKET}/{CODE_PREFIX}/{CODE_VERSION}'

GLUE_REGION = 'us-west-1'
GLUE_ROLE_NAME = 'sfly-aws-dwh-sandbox-jc-glue'
GLUE_CONNECTION_NAME = 'sfly-aws-dwh-sandbox-jc-postgres-connection'

JOB_EVENTS_SNS_TOPIC = "arn:aws:sns:us-west-1:542605267262:dwh-pipeline-events-jc"

DATA_BUCKET = 'sfly-aws-dwh-sandbox-jc-data-us-west-1'
S3_DATA_SOURCE = Variable.get('S3_IMAGE_SOURCE', f's3://{DATA_BUCKET}/images/source')
S3_DATA_SINK = Variable.get('S3_IMAGE_SINK', f's3://{DATA_BUCKET}/images/sink')

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
        '--module_name': 'dwh.jobs.transform_images.transform_images_job_factory',
        '--transform_images_job': json.dumps({
            "extractor_config": {
                "path": S3_DATA_SOURCE
            },
            "loader_config": {
                "path": S3_DATA_SINK
            },
            "event_publisher_config": {
                "publisher_type": "SNS",
                "region": GLUE_REGION,
                "topic_arn": JOB_EVENTS_SNS_TOPIC
            },
            "quality_checker_config": {
                "drop_rate_yellow": 0.05,
                "drop_rate_red": 0.10,
                "min_records": 0
            },
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
            '--extra-jars': (
                f"{S3_CODE_PATH}/jars/decryption-udfs_2.12-1.0.0.jar,"
                f"{S3_CODE_PATH}/jars/platform.infrastructure-1.19.5-SNAPSHOT.jar"
            ),
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

wait_for_glue_job = GlueJobSensor(
    task_id='wait_for_glue_job',
    job_name=f"{DAG_ID}_{CODE_VERSION}",
    run_id="{{ task_instance.xcom_pull(task_ids='glue_job', key='return_value') }}",
    dag=dag
)

run_glue_job >> wait_for_glue_job
