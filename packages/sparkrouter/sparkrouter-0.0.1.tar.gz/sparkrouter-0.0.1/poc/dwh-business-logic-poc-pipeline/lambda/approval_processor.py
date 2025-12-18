"""
Lambda function to process human approval decisions.

This function handles approval events from the job_approvals topic, updating
the original job event in OpenSearch and creating an audit trail.

Expected event structure:
{
    "event_type": "approval_decision",
    "job_name": str,
    "job_run_id": str,
    "timestamp": str,              # ISO timestamp
    "decision": str,               # APPROVED, REJECTED
    "decided_by": str,             # Email or user ID
    "reason": str                  # Explanation for the decision
}

Actions:
1. Find original job event in OpenSearch by job_run_id
2. Update document with approval fields
3. Index approval event separately for audit trail

Environment Variables:
    OPENSEARCH_ENDPOINT: OpenSearch domain endpoint
    REGION: AWS region
"""

import json
import os
import boto3
from datetime import datetime, timezone
from typing import Dict, Any
import hashlib

from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

# OpenSearch configuration
OPENSEARCH_ENDPOINT = os.environ['OPENSEARCH_ENDPOINT']
REGION = os.environ.get('REGION', 'us-west-1')

# Index names
JOB_EVENTS_INDEX = 'job-events'
JOB_APPROVALS_INDEX = 'job-approvals'


def get_opensearch_client():
    """Create and return OpenSearch client with AWS IAM auth."""
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        REGION,
        'es',
        session_token=credentials.token
    )

    return OpenSearch(
        hosts=[{'host': OPENSEARCH_ENDPOINT, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing approval decisions from SNS.

    Args:
        event: SNS event containing approval decision JSON
        context: Lambda context

    Returns:
        Response dict with status and message
    """
    print(f"Received event: {json.dumps(event)}")

    try:
        # Check if this is an SNS event
        if 'Records' in event and event['Records']:
            sns_record = event['Records'][0]
            if sns_record.get('EventSource') == 'aws:sns':
                event_json = sns_record['Sns']['Message']
                print(f"SNS Message: {event_json}")
                approval_event = json.loads(event_json)
            else:
                return {'statusCode': 400, 'body': f"Unknown event source: {sns_record.get('EventSource')}"}
        else:
            # Direct invocation for testing
            print("Direct invocation - processing event directly")
            approval_event = event

        job_name = approval_event.get('job_name', 'unknown')
        job_run_id = approval_event.get('job_run_id', '')
        decision = approval_event.get('decision', '')
        decided_by = approval_event.get('decided_by', '')
        reason = approval_event.get('reason', '')
        timestamp = approval_event.get('timestamp') or datetime.now(timezone.utc).isoformat()

        # Validate required fields
        if not job_run_id:
            return {'statusCode': 400, 'body': 'Missing required field: job_run_id'}
        if decision not in ['APPROVED', 'REJECTED']:
            return {'statusCode': 400, 'body': f'Invalid decision: {decision}. Must be APPROVED or REJECTED'}

        # Update original job event in both indexes
        update_job_event(job_name, job_run_id, decision, decided_by, reason, timestamp)

        # Create audit trail entry
        audit_doc = create_audit_document(approval_event, timestamp)
        index_document(audit_doc, JOB_APPROVALS_INDEX)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully processed approval',
                'job_name': job_name,
                'job_run_id': job_run_id,
                'decision': decision,
                'decided_by': decided_by
            })
        }

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        raise


def update_job_event(
    job_name: str,
    job_run_id: str,
    decision: str,
    decided_by: str,
    reason: str,
    timestamp: str
) -> None:
    """
    Update original job event with approval information.

    Updates both the common index and job-specific index.
    """
    client = get_opensearch_client()

    update_body = {
        'doc': {
            'approval_status': decision,
            'approved_by': decided_by,
            'approval_reason': reason,
            'approval_timestamp': timestamp
        }
    }

    # Find and update in common index
    try:
        search_result = client.search(
            index=JOB_EVENTS_INDEX,
            body={
                'query': {
                    'bool': {
                        'must': [
                            {'term': {'job_run_id': job_run_id}},
                            {'term': {'job_name': job_name}}
                        ]
                    }
                }
            }
        )

        hits = search_result.get('hits', {}).get('hits', [])
        if hits:
            doc_id = hits[0]['_id']
            client.update(index=JOB_EVENTS_INDEX, id=doc_id, body=update_body)
            print(f"Updated job event in {JOB_EVENTS_INDEX}: {doc_id}")
        else:
            print(f"Warning: No job event found for job_run_id={job_run_id} in {JOB_EVENTS_INDEX}")

    except Exception as e:
        print(f"Error updating {JOB_EVENTS_INDEX}: {e}")

    # Find and update in job-specific index
    job_index = f"job-events-{job_name.lower().replace('_', '-')}"
    try:
        search_result = client.search(
            index=job_index,
            body={
                'query': {
                    'term': {'job_run_id': job_run_id}
                }
            }
        )

        hits = search_result.get('hits', {}).get('hits', [])
        if hits:
            doc_id = hits[0]['_id']
            client.update(index=job_index, id=doc_id, body=update_body)
            print(f"Updated job event in {job_index}: {doc_id}")
        else:
            print(f"Warning: No job event found for job_run_id={job_run_id} in {job_index}")

    except Exception as e:
        print(f"Error updating {job_index}: {e}")


def create_audit_document(approval_event: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    """Create audit trail document for the approval."""
    job_name = approval_event.get('job_name', 'unknown')
    job_run_id = approval_event.get('job_run_id', '')

    doc_id = hashlib.sha256(
        f"{job_name}|{job_run_id}|APPROVAL|{timestamp}".encode()
    ).hexdigest()[:16]

    return {
        'id': doc_id,
        'timestamp': timestamp,
        'event_type': 'approval_decision',
        'job_name': job_name,
        'job_run_id': job_run_id,
        'decision': approval_event.get('decision'),
        'decided_by': approval_event.get('decided_by'),
        'reason': approval_event.get('reason'),
    }


def index_document(document: Dict[str, Any], index: str) -> None:
    """Index document to OpenSearch."""
    client = get_opensearch_client()

    # Create index if it doesn't exist
    if not client.indices.exists(index=index):
        create_approvals_index(client, index)

    doc_id = document.get('id')
    response = client.index(
        index=index,
        id=doc_id,
        body=document,
        refresh=True
    )
    print(f"Indexed document to {index}: {doc_id}, result: {response.get('result')}")


def create_approvals_index(client, index: str) -> None:
    """Create the job-approvals index with appropriate mappings."""
    index_body = {
        'settings': {
            'number_of_shards': 1,
            'number_of_replicas': 1,
        },
        'mappings': {
            'properties': {
                'timestamp': {'type': 'date'},
                'event_type': {'type': 'keyword'},
                'job_name': {'type': 'keyword'},
                'job_run_id': {'type': 'keyword'},
                'decision': {'type': 'keyword'},
                'decided_by': {'type': 'keyword'},
                'reason': {'type': 'text'},
            }
        }
    }

    response = client.indices.create(index=index, body=index_body)
    print(f"Created index: {index}, response: {response}")
