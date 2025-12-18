"""
Lambda function to trigger downstream jobs/workflows.

This function listens to:
1. job_events topic (filtered: status = SUCCESS) - trigger on successful job completion
2. job_approvals topic (filtered: decision = APPROVED) - trigger on approval of quality failures

Actions:
1. Look up workflow configuration for the job
2. Determine next step(s) in the pipeline
3. Trigger next job(s) via Glue, Step Functions, or EventBridge

Environment Variables:
    REGION: AWS region
    WORKFLOW_CONFIG_S3_URI: S3 URI for workflow config JSON (e.g., s3://bucket/config/workflow_config.json)
    WORKFLOW_CONFIG_PARAM: SSM Parameter Store path for workflow config (fallback, optional)
"""

import json
import os
import boto3
from typing import Dict, Any, List

# Configuration
REGION = os.environ.get('REGION', 'us-west-1')
WORKFLOW_CONFIG_S3_URI = os.environ.get('WORKFLOW_CONFIG_S3_URI', '')
WORKFLOW_CONFIG_PARAM = os.environ.get('WORKFLOW_CONFIG_PARAM', '')
MWAA_TRIGGER_QUEUE_URL = os.environ.get('MWAA_TRIGGER_QUEUE_URL', '')

# AWS clients
s3_client = boto3.client('s3', region_name=REGION)
glue_client = boto3.client('glue', region_name=REGION)
sfn_client = boto3.client('stepfunctions', region_name=REGION)
events_client = boto3.client('events', region_name=REGION)
ssm_client = boto3.client('ssm', region_name=REGION)
sqs_client = boto3.client('sqs', region_name=REGION)

# Default workflow configuration (can be overridden via SSM Parameter Store)
DEFAULT_WORKFLOW_CONFIG = {
    # Example configuration - customize per job
    # "transform_images": {
    #     "on_success": [
    #         {"type": "glue_job", "job_name": "load_to_redshift"},
    #         {"type": "step_function", "arn": "arn:aws:states:us-west-1:123456789:stateMachine:my-workflow"}
    #     ]
    # }
}


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for orchestrating downstream jobs.

    Handles both:
    - Job completion events (status = SUCCESS)
    - Approval events (decision = APPROVED)

    Args:
        event: SNS event containing job event or approval JSON
        context: Lambda context

    Returns:
        Response dict with status and triggered jobs
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Parse SNS message
        if 'Records' in event and event['Records']:
            sns_record = event['Records'][0]
            if sns_record.get('EventSource') == 'aws:sns':
                event_json = sns_record['Sns']['Message']
                print(f"SNS Message: {event_json}")
                payload = json.loads(event_json)
            else:
                return {'statusCode': 400, 'body': f"Unknown event source: {sns_record.get('EventSource')}"}
        else:
            # Direct invocation for testing
            print("Direct invocation - processing event directly")
            payload = event

        # Determine event type and extract job info
        event_type = payload.get('event_type', '')
        job_name = payload.get('job_name', 'unknown')
        job_run_id = payload.get('job_run_id', '')

        # Validate this is a triggerable event
        if event_type == 'job_completed':
            status = payload.get('status', '')
            if status != 'SUCCESS':
                print(f"Skipping non-SUCCESS job event: status={status}")
                return {'statusCode': 200, 'body': 'Skipped: not a SUCCESS event'}
        elif event_type == 'approval_decision':
            decision = payload.get('decision', '')
            if decision != 'APPROVED':
                print(f"Skipping non-APPROVED decision: decision={decision}")
                return {'statusCode': 200, 'body': 'Skipped: not an APPROVED decision'}
        else:
            print(f"Unknown event type: {event_type}")
            return {'statusCode': 400, 'body': f'Unknown event type: {event_type}'}

        # Get workflow configuration
        workflow_config = get_workflow_config()

        # Support both flat structure and nested 'workflows' key
        workflows = workflow_config.get('workflows', workflow_config)
        job_config = workflows.get(job_name, {})

        if not job_config:
            print(f"No workflow configuration found for job: {job_name}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No downstream jobs configured',
                    'job_name': job_name
                })
            }

        # Determine which triggers to use based on event type
        if event_type == 'approval_decision':
            # Use on_approval if defined, otherwise fall back to on_success
            downstream_jobs = job_config.get('on_approval', job_config.get('on_success', []))
        else:
            downstream_jobs = job_config.get('on_success', [])

        triggered = []
        errors = []

        for downstream in downstream_jobs:
            try:
                result = trigger_downstream(downstream, job_name, job_run_id, payload)
                triggered.append(result)
                print(f"Triggered: {result}")
            except Exception as e:
                error_msg = f"Failed to trigger {downstream}: {e}"
                print(error_msg)
                errors.append(error_msg)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Orchestration complete',
                'job_name': job_name,
                'job_run_id': job_run_id,
                'triggered': triggered,
                'errors': errors
            })
        }

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        raise


def get_workflow_config() -> Dict[str, Any]:
    """
    Get workflow configuration from S3, SSM Parameter Store, or use defaults.

    Priority:
    1. S3 (WORKFLOW_CONFIG_S3_URI) - preferred for version control
    2. SSM Parameter Store (WORKFLOW_CONFIG_PARAM) - fallback
    3. DEFAULT_WORKFLOW_CONFIG - hardcoded default

    Returns:
        Workflow configuration dictionary
    """
    # Try S3 first (preferred)
    if WORKFLOW_CONFIG_S3_URI:
        try:
            config = load_config_from_s3(WORKFLOW_CONFIG_S3_URI)
            print(f"Loaded workflow config from S3: {WORKFLOW_CONFIG_S3_URI}")
            return config
        except Exception as e:
            print(f"Failed to load workflow config from S3: {e}")

    # Fallback to SSM Parameter Store
    if WORKFLOW_CONFIG_PARAM:
        try:
            response = ssm_client.get_parameter(
                Name=WORKFLOW_CONFIG_PARAM,
                WithDecryption=True
            )
            print(f"Loaded workflow config from SSM: {WORKFLOW_CONFIG_PARAM}")
            return json.loads(response['Parameter']['Value'])
        except Exception as e:
            print(f"Failed to load workflow config from SSM: {e}")

    print("Using default workflow config")
    return DEFAULT_WORKFLOW_CONFIG


def get_nested_value(obj: Dict[str, Any], path: str) -> Any:
    """
    Extract a value from a nested dictionary using dot notation.

    Args:
        obj: Dictionary to extract from
        path: Dot-separated path (e.g., "metrics.start_date", "artifacts.output_path")

    Returns:
        Value at path, or None if path doesn't exist
    """
    keys = path.split('.')
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current


def load_config_from_s3(s3_uri: str) -> Dict[str, Any]:
    """
    Load JSON configuration from S3.

    Args:
        s3_uri: S3 URI (e.g., s3://bucket/path/config.json)

    Returns:
        Parsed JSON configuration
    """
    # Parse S3 URI
    if not s3_uri.startswith('s3://'):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")

    path = s3_uri[5:]  # Remove 's3://'
    bucket = path.split('/')[0]
    key = '/'.join(path.split('/')[1:])

    response = s3_client.get_object(Bucket=bucket, Key=key)
    content = response['Body'].read().decode('utf-8')
    return json.loads(content)


def trigger_downstream(
    config: Dict[str, Any],
    source_job: str,
    source_run_id: str,
    source_event: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Trigger a downstream job based on configuration.

    Args:
        config: Downstream job configuration
        source_job: Name of the job that triggered this
        source_run_id: Run ID of the source job
        source_event: Full event from source job

    Returns:
        Result dictionary with trigger details
    """
    trigger_type = config.get('type', '')

    if trigger_type == 'glue_job':
        return trigger_glue_job(config, source_job, source_run_id, source_event)
    elif trigger_type == 'step_function':
        return trigger_step_function(config, source_job, source_run_id, source_event)
    elif trigger_type == 'eventbridge':
        return trigger_eventbridge(config, source_job, source_run_id, source_event)
    elif trigger_type == 'sqs_mwaa':
        return trigger_sqs_mwaa(config, source_job, source_run_id, source_event)
    else:
        raise ValueError(f"Unknown trigger type: {trigger_type}")


def trigger_glue_job(
    config: Dict[str, Any],
    source_job: str,
    source_run_id: str,
    source_event: Dict[str, Any]
) -> Dict[str, Any]:
    """Trigger an AWS Glue job."""
    job_name = config.get('job_name')
    if not job_name:
        raise ValueError("Glue job config missing 'job_name'")

    # Build arguments from config and source event
    arguments = config.get('arguments', {}).copy()
    arguments['--triggered_by_job'] = source_job
    arguments['--triggered_by_run_id'] = source_run_id

    # Pass through artifacts if available
    artifacts = source_event.get('artifacts', {})
    if artifacts:
        arguments['--source_artifacts'] = json.dumps(artifacts)

    response = glue_client.start_job_run(
        JobName=job_name,
        Arguments=arguments
    )

    return {
        'type': 'glue_job',
        'job_name': job_name,
        'run_id': response['JobRunId']
    }


def trigger_step_function(
    config: Dict[str, Any],
    source_job: str,
    source_run_id: str,
    source_event: Dict[str, Any]
) -> Dict[str, Any]:
    """Trigger an AWS Step Functions state machine."""
    state_machine_arn = config.get('arn')
    if not state_machine_arn:
        raise ValueError("Step function config missing 'arn'")

    # Build input from source event
    input_data = {
        'triggered_by_job': source_job,
        'triggered_by_run_id': source_run_id,
        'source_event': source_event
    }

    # Generate unique execution name
    import hashlib
    from datetime import datetime
    execution_name = hashlib.sha256(
        f"{source_job}|{source_run_id}|{datetime.utcnow().isoformat()}".encode()
    ).hexdigest()[:20]

    response = sfn_client.start_execution(
        stateMachineArn=state_machine_arn,
        name=f"{source_job}-{execution_name}",
        input=json.dumps(input_data)
    )

    return {
        'type': 'step_function',
        'arn': state_machine_arn,
        'execution_arn': response['executionArn']
    }


def trigger_eventbridge(
    config: Dict[str, Any],
    source_job: str,
    source_run_id: str,
    source_event: Dict[str, Any]
) -> Dict[str, Any]:
    """Publish event to EventBridge for further routing."""
    event_bus = config.get('event_bus', 'default')
    detail_type = config.get('detail_type', 'Job Downstream Trigger')
    source = config.get('source', 'dwh.orchestrator')

    detail = {
        'triggered_by_job': source_job,
        'triggered_by_run_id': source_run_id,
        'source_event': source_event
    }

    response = events_client.put_events(
        Entries=[
            {
                'Source': source,
                'DetailType': detail_type,
                'Detail': json.dumps(detail),
                'EventBusName': event_bus
            }
        ]
    )

    failed = response.get('FailedEntryCount', 0)
    if failed > 0:
        raise Exception(f"Failed to publish {failed} events to EventBridge")

    return {
        'type': 'eventbridge',
        'event_bus': event_bus,
        'detail_type': detail_type
    }


def trigger_sqs_mwaa(
    config: Dict[str, Any],
    source_job: str,
    source_run_id: str,
    source_event: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Publish a structured message to SQS for MWAA to consume.

    This trigger type is used when MWAA has private networking and cannot
    be triggered directly via the REST API. Instead, we publish a message
    to an SQS queue that MWAA's event_dispatcher DAG polls.

    The message contains:
        dag_id: Which DAG to trigger
        conf: Parameters to pass to the DAG (built from parameter_mapping)

    Config fields:
        queue_url: SQS queue URL (optional, defaults to MWAA_TRIGGER_QUEUE_URL env var)
        dag_id: DAG ID to trigger (required)
        conf: Static configuration to pass to DAG (optional)
        parameter_mapping: Map of DAG param -> event field path (optional)
    """
    queue_url = config.get('queue_url') or MWAA_TRIGGER_QUEUE_URL
    if not queue_url:
        raise ValueError("sqs_mwaa config missing 'queue_url' and MWAA_TRIGGER_QUEUE_URL env var not set")

    dag_id = config.get('dag_id')
    if not dag_id:
        raise ValueError("sqs_mwaa config missing 'dag_id'")

    # Build DAG configuration from static conf + parameter mappings
    dag_conf = config.get('conf', {}).copy()

    # Always include trigger metadata
    dag_conf['triggered_by_job'] = source_job
    dag_conf['triggered_by_run_id'] = source_run_id

    # Apply parameter mappings from config (event field -> DAG parameter)
    parameter_mapping = config.get('parameter_mapping', {})
    for dag_param, event_path in parameter_mapping.items():
        value = get_nested_value(source_event, event_path)
        if value is not None:
            dag_conf[dag_param] = value

    # Build the SQS message payload
    # This is what the event_dispatcher DAG expects
    message_body = {
        'dag_id': dag_id,
        'conf': dag_conf
    }

    # Send to SQS
    response = sqs_client.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(message_body),
        MessageAttributes={
            'dag_id': {
                'DataType': 'String',
                'StringValue': dag_id
            },
            'source_job': {
                'DataType': 'String',
                'StringValue': source_job
            }
        }
    )

    return {
        'type': 'sqs_mwaa',
        'queue_url': queue_url,
        'dag_id': dag_id,
        'message_id': response['MessageId']
    }
