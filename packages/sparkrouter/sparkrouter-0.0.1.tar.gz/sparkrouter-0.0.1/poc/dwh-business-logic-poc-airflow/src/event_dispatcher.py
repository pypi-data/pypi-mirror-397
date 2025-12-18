"""
Event Dispatcher DAG

A generic dispatcher that polls an SQS queue for DAG trigger messages
and triggers the specified DAGs with the provided configuration.

Architecture:
    Job completes -> SNS -> Lambda Orchestrator -> SQS -> This DAG -> Target DAG
                                ↓
                        workflow_config.json
                        (dag_id + parameter_mapping)

Message Format (from orchestrator):
    {
        "dag_id": "filter_image_glue_pyspark",
        "conf": {
            "triggered_by_job": "transform_images",
            "triggered_by_run_id": "spark-xxx",
            "start_date": "2025-01-01",
            "end_date": "2025-01-02",
            ...
        }
    }

This DAG is completely generic - it has no knowledge of specific jobs or DAGs.
All routing and parameter mapping is handled by the orchestrator lambda.
"""

from datetime import datetime, timedelta
import json
from airflow import DAG
from airflow.models import Variable
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.sqs import SqsSensor
from airflow.providers.amazon.aws.hooks.sqs import SqsHook


def get_queue_url():
    """Get SQS queue URL from Airflow Variable."""
    return Variable.get("mwaa_trigger_queue_url")


# SQS Queue URL template for sensor (supports Jinja)
SQS_QUEUE_URL_TEMPLATE = "{{ var.value.mwaa_trigger_queue_url }}"

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'retries': 0,  # SQS handles retries via visibility timeout; new DAG run every minute
}


def dispatch_events(**context):
    """
    Process SQS messages and trigger the specified DAGs.

    Each message contains:
        dag_id: Which DAG to trigger
        conf: Configuration/parameters to pass to the DAG
    """
    ti = context['ti']
    messages = ti.xcom_pull(task_ids='wait_for_events', key='messages')

    if not messages:
        print("No messages to process")
        return []

    sqs_hook = SqsHook()
    triggered_dags = []
    queue_url = get_queue_url()

    print(f"Processing {len(messages)} message(s) from queue: {queue_url}")

    for message in messages:
        receipt_handle = message.get('ReceiptHandle')

        try:
            # Parse the message body
            body = json.loads(message['Body'])

            dag_id = body.get('dag_id')
            conf = body.get('conf', {})

            if not dag_id:
                print(f"Message missing 'dag_id', skipping: {body}")
                delete_message(sqs_hook, queue_url, receipt_handle)
                continue

            print(f"Triggering DAG: {dag_id}")
            print(f"Configuration: {json.dumps(conf, indent=2)}")

            # Trigger the DAG using Airflow's API
            from airflow.api.common.trigger_dag import trigger_dag

            # Generate a unique run_id
            source_job = conf.get('triggered_by_job', 'unknown')
            source_run = conf.get('triggered_by_run_id', 'unknown')
            run_id = f"dispatched__{source_job}__{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"

            trigger_dag(
                dag_id=dag_id,
                run_id=run_id,
                conf=conf,
                replace_microseconds=False,
            )

            triggered_dags.append({
                'dag_id': dag_id,
                'run_id': run_id,
                'source_job': source_job,
                'source_run_id': source_run,
            })

            print(f"Successfully triggered {dag_id} with run_id={run_id}")

            # Delete the message from SQS after successful processing
            delete_message(sqs_hook, queue_url, receipt_handle)

        except Exception as e:
            print(f"Error processing message: {e}")
            print(f"Message body: {message.get('Body')}")
            # Don't delete - let it retry via SQS visibility timeout
            # After max retries, it will go to DLQ
            raise

    print(f"Dispatch complete. Triggered {len(triggered_dags)} DAGs.")
    return triggered_dags


def delete_message(sqs_hook: SqsHook, queue_url: str, receipt_handle: str):
    """Delete a processed message from SQS."""
    if receipt_handle:
        sqs_hook.get_conn().delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=receipt_handle
        )
        print("Deleted message from SQS")


with DAG(
    'event_dispatcher',
    default_args=default_args,
    description='Generic dispatcher: polls SQS and triggers DAGs with provided config',
    schedule_interval=timedelta(minutes=1),
    catchup=False,
    max_active_runs=1,
    tags=['dispatcher', 'orchestration'],
) as dag:

    # Wait for messages on the SQS queue
    wait_for_events = SqsSensor(
        task_id='wait_for_events',
        sqs_queue=SQS_QUEUE_URL_TEMPLATE,
        max_messages=10,
        wait_time_seconds=20,
        visibility_timeout=300,
        mode='reschedule',
        poke_interval=30,
        timeout=60,
        soft_fail=True,
    )

    # Process messages and trigger DAGs
    dispatch = PythonOperator(
        task_id='dispatch_events',
        python_callable=dispatch_events,
        provide_context=True,
    )

    wait_for_events >> dispatch
