"""
Lambda function to index job events into OpenSearch.

This function handles job events from JobEventPublisher, indexing them to:
1. A common index (job-events) for cross-job dashboards
2. A job-specific index (job-events-{job_name}) for deep-dive analysis

IMPORTANT: Both indices use the SAME natural structure from JobEventPublisher.
This ensures consistent field paths (e.g., metrics.duration_seconds) across all indices,
minimizing cognitive overhead when building dashboards and scripted fields.

The only difference:
- Common index: excludes metrics.payload (job-specific fields)
- Job-specific index: includes everything

Expected event structure (from JobEventPublisher / AbstractJobMetrics.get_json()):
{
    "event_type": "job_completed",
    "job_name": str,
    "job_run_id": str,
    "timestamp": str,
    "status": str,                 # SUCCESS, PENDING_APPROVAL, FAILED
    "failure_type": str | null,    # CATASTROPHIC, QUALITY, or null
    "artifacts_available": bool,
    "artifacts": {...},
    "quality": {
        "status": str,             # GREEN, YELLOW, RED
        "checks": [...]
    },
    "metrics": {
        "duration_seconds": float,
        "records_read": int,
        "records_written": int,
        "records_dropped": int,
        "bytes_written": int,
        "phases": {
            "extract": {"duration_seconds": float, ...},
            "transform": {"duration_seconds": float, ...},
            "load": {"duration_seconds": float, ...}
        },
        "drop_reasons": [{"reason": str, "count": int}, ...],
        "payload": {...}           # Job-specific (only in job-specific index)
    },
    "error": {...} | null
}

Environment Variables:
    OPENSEARCH_ENDPOINT: OpenSearch domain endpoint
    OPENSEARCH_INDEX_COMMON: Common index name (default: job-events)
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
OPENSEARCH_INDEX_COMMON = os.environ.get('OPENSEARCH_INDEX_COMMON', 'job-events')
REGION = os.environ.get('REGION', 'us-west-1')


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


# Track if template has been ensured this invocation
_template_ensured = False


def ensure_index_template(client) -> None:
    """
    Ensure index template exists for job-events-* indices.

    This template pre-defines mappings for fields that might have type
    ambiguity (e.g., threshold: 0 vs 0.05). Without this, OpenSearch's
    dynamic mapping might infer wrong types from the first document.
    """
    global _template_ensured
    if _template_ensured:
        return

    template_name = "job-events-template"

    # Check if template exists
    try:
        client.indices.get_index_template(name=template_name)
        _template_ensured = True
        return
    except Exception:
        pass  # Template doesn't exist, create it

    template_body = {
        "index_patterns": ["job-events*"],
        "priority": 100,
        "template": {
            "settings": {
                "number_of_shards": 2,
                "number_of_replicas": 1,
                "index.refresh_interval": "5s"
            },
            "mappings": {
                "dynamic": True,
                "properties": {
                    # === Document identity ===
                    "id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "event_type": {"type": "keyword"},

                    # === Job identity ===
                    "job_name": {"type": "keyword"},
                    "job_run_id": {"type": "keyword"},

                    # === Status ===
                    "status": {"type": "keyword"},
                    "failure_type": {"type": "keyword"},

                    # === Quality (natural structure) ===
                    "quality": {
                        "properties": {
                            "status": {"type": "keyword"},
                            "checks": {
                                "type": "nested",
                                "properties": {
                                    "name": {"type": "keyword"},
                                    "status": {"type": "keyword"},
                                    "value": {"type": "float"},
                                    "threshold": {"type": "float"},
                                    "message": {"type": "text"}
                                }
                            }
                        }
                    },

                    # === Metrics (natural structure from AbstractJobMetrics.get_json()) ===
                    # Both indices use this same structure for consistent field paths
                    "metrics": {
                        "properties": {
                            "job_name": {"type": "keyword"},
                            "job_run_id": {"type": "keyword"},
                            "job_status": {"type": "keyword"},
                            "start_time": {"type": "date"},
                            "end_time": {"type": "date"},
                            "duration_seconds": {"type": "float"},
                            "service_provider": {"type": "keyword"},
                            "environment": {"type": "keyword"},
                            "region": {"type": "keyword"},
                            "created_by": {"type": "keyword"},
                            "start_date": {"type": "keyword"},
                            "end_date": {"type": "keyword"},
                            "source_base_path": {"type": "keyword"},
                            "sink_base_path": {"type": "keyword"},
                            "records_read": {"type": "long"},
                            "records_written": {"type": "long"},
                            "records_dropped": {"type": "long"},
                            "bytes_written": {"type": "long"},
                            "drop_reasons": {
                                "type": "nested",
                                "properties": {
                                    "reason": {"type": "keyword"},
                                    "count": {"type": "long"}
                                }
                            },
                            "phases": {
                                "properties": {
                                    "extract": {
                                        "properties": {
                                            "duration_seconds": {"type": "float"},
                                            "start_time": {"type": "date"},
                                            "end_time": {"type": "date"}
                                        }
                                    },
                                    "transform": {
                                        "properties": {
                                            "duration_seconds": {"type": "float"},
                                            "start_time": {"type": "date"},
                                            "end_time": {"type": "date"}
                                        }
                                    },
                                    "load": {
                                        "properties": {
                                            "duration_seconds": {"type": "float"},
                                            "start_time": {"type": "date"},
                                            "end_time": {"type": "date"}
                                        }
                                    }
                                }
                            },
                            # Job-specific payload (only in job-specific index)
                            "payload": {
                                "properties": {
                                    "transform": {
                                        "properties": {
                                            "data_types": {
                                                "type": "nested",
                                                "properties": {
                                                    "name": {"type": "keyword"},
                                                    "records": {"type": "long"},
                                                    "dropped": {"type": "long"}
                                                }
                                            }
                                        }
                                    },
                                    "load": {
                                        "properties": {
                                            "bytes_by_category": {
                                                "type": "nested",
                                                "properties": {
                                                    "category": {"type": "keyword"},
                                                    "bytes": {"type": "long"}
                                                }
                                            },
                                            "output_summary": {
                                                "type": "nested",
                                                "properties": {
                                                    "category": {"type": "keyword"},
                                                    "file_count": {"type": "integer"},
                                                    "bytes": {"type": "long"},
                                                    "base_path": {"type": "keyword"}
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    },

                    # === Error (natural structure) ===
                    "error": {
                        "properties": {
                            "type": {"type": "keyword"},
                            "message": {"type": "text"},
                            "stack_trace": {"type": "text"}
                        }
                    },

                    # === Approval tracking ===
                    "approval_status": {"type": "keyword"},
                    "approved_by": {"type": "keyword"},
                    "approval_reason": {"type": "text"},
                    "approval_timestamp": {"type": "date"},
                }
            }
        }
    }

    try:
        client.indices.put_index_template(name=template_name, body=template_body)
        print(f"Created index template: {template_name}")
    except Exception as e:
        print(f"Warning: Could not create index template: {e}")

    _template_ensured = True


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for processing job events from SNS.

    Indexes events to both:
    - Common index for cross-job comparison
    - Job-specific index for detailed analysis

    Args:
        event: SNS event containing job event JSON
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
                # Parse SNS message body
                event_json = sns_record['Sns']['Message']
                print(f"SNS Message: {event_json}")
                job_event = json.loads(event_json)
            else:
                return {'statusCode': 400, 'body': f"Unknown event source: {sns_record.get('EventSource')}"}
        else:
            # Direct invocation for testing
            print("Direct invocation - processing event directly")
            job_event = event

        # Process and index event
        job_name = job_event.get('job_name', 'unknown')
        common_doc, job_doc = process_job_event(job_event)

        # Index to common index (for cross-job dashboards)
        index_to_opensearch(common_doc, index=OPENSEARCH_INDEX_COMMON)

        # Index to job-specific index (for deep-dive analysis)
        job_index = get_job_specific_index(job_name)
        index_to_opensearch(job_doc, index=job_index)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Successfully indexed job event',
                'job_name': job_name,
                'status': job_event.get('status'),
                'common_index': OPENSEARCH_INDEX_COMMON,
                'job_index': job_index,
                'document_id': common_doc.get('id')
            })
        }

    except Exception as e:
        print(f"Error processing event: {str(e)}")
        print(f"Event: {json.dumps(event)}")
        raise


def get_job_specific_index(job_name: str) -> str:
    """
    Generate job-specific index name.

    Args:
        job_name: Name of the job (e.g., 'transform_images')

    Returns:
        Index name (e.g., 'job-events-transform-images')
    """
    normalized = job_name.lower().replace('_', '-')
    return f"job-events-{normalized}"


def process_job_event(job_event: Dict[str, Any]) -> tuple:
    """
    Process job event into documents for OpenSearch indexing.

    Both documents use the SAME natural structure from JobEventPublisher.
    This ensures consistent field paths across all indices (e.g., metrics.duration_seconds).

    Returns two documents:
    1. Common document - core fields for cross-job comparison (subset of full event)
    2. Job document - full event for job-specific deep-dive analysis

    Args:
        job_event: Job event dict from JobEventPublisher

    Returns:
        Tuple of (common_document, job_document)
    """
    job_name = job_event.get('job_name', 'unknown')
    job_run_id = job_event.get('job_run_id', '')
    timestamp = job_event.get('timestamp') or datetime.now(timezone.utc).isoformat()

    # Extract nested structures for convenience fields
    quality = job_event.get('quality', {})
    error = job_event.get('error')

    # Generate unique document ID
    doc_id = generate_doc_id(job_name, job_run_id, job_event.get('status', 'UNKNOWN'), timestamp)

    # Common document - uses natural structure from JobEventPublisher
    # Only includes fields that ALL jobs have (no job-specific payload)
    common_doc = {
        'id': doc_id,
        'timestamp': timestamp,
        'event_type': job_event.get('event_type', 'job_completed'),

        # Job identity
        'job_name': job_name,
        'job_run_id': job_run_id,

        # Status
        'status': job_event.get('status'),
        'failure_type': job_event.get('failure_type'),

        # Quality - pass through natural structure
        'quality': quality,

        # Artifacts
        'artifacts_available': job_event.get('artifacts_available', False),
        'artifacts': job_event.get('artifacts', {}),

        # Metrics - pass through natural structure (WITHOUT job-specific payload)
        # This preserves paths like metrics.duration_seconds, metrics.records_written
        'metrics': _extract_common_metrics(job_event.get('metrics', {})),

        # Error - pass through natural structure
        'error': error,

        # Approval tracking (populated later by approval_processor)
        'approval_status': None,
        'approved_by': None,
        'approval_reason': None,
        'approval_timestamp': None,
    }

    # Job-specific document - full event pass-through
    # Includes everything: metrics.payload with job-specific fields
    job_doc = {
        **job_event,
        'id': doc_id,
        'timestamp': timestamp,

        # Approval tracking (populated later by approval_processor)
        'approval_status': None,
        'approved_by': None,
        'approval_reason': None,
        'approval_timestamp': None,
    }

    return common_doc, job_doc


def _extract_common_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract common metrics fields (excluding job-specific payload).

    This ensures the common index only has fields that ALL jobs share,
    while preserving the natural nested structure.

    Args:
        metrics: Full metrics dict from job event

    Returns:
        Metrics dict with only common fields (no payload)
    """
    return {
        'job_name': metrics.get('job_name'),
        'job_run_id': metrics.get('job_run_id'),
        'job_status': metrics.get('job_status'),
        'start_time': metrics.get('start_time'),
        'end_time': metrics.get('end_time'),
        'duration_seconds': metrics.get('duration_seconds', 0),
        'service_provider': metrics.get('service_provider'),
        'environment': metrics.get('environment'),
        'region': metrics.get('region'),
        'created_by': metrics.get('created_by'),
        'start_date': metrics.get('start_date'),
        'end_date': metrics.get('end_date'),
        'source_base_path': metrics.get('source_base_path'),
        'sink_base_path': metrics.get('sink_base_path'),
        'records_read': metrics.get('records_read', 0),
        'records_written': metrics.get('records_written', 0),
        'records_dropped': metrics.get('records_dropped', 0),
        'bytes_written': metrics.get('bytes_written', 0),
        'phases': metrics.get('phases', {}),
        'drop_reasons': metrics.get('drop_reasons', []),
        # Explicitly exclude 'payload' - that's job-specific
    }


def generate_doc_id(job_name: str, job_run_id: str, status: str, timestamp: str) -> str:
    """
    Generate a unique document ID for OpenSearch.

    Args:
        job_name: Job name
        job_run_id: Job run ID
        status: Job status
        timestamp: Event timestamp

    Returns:
        Unique document ID
    """
    components = f"{job_name}|{job_run_id}|{status}|{timestamp}"
    hash_obj = hashlib.sha256(components.encode())
    return hash_obj.hexdigest()[:16]


def index_to_opensearch(document: Dict[str, Any], index: str) -> None:
    """
    Index document to OpenSearch.

    Args:
        document: Document to index
        index: Target index name
    """
    client = get_opensearch_client()

    # Ensure index template exists (defines types for ambiguous fields)
    ensure_index_template(client)

    # Create index if it doesn't exist (template will apply automatically)
    if not client.indices.exists(index=index):
        create_index(client, index)

    # Index document
    doc_id = document.get('id')
    response = client.index(
        index=index,
        id=doc_id,
        body=document,
        refresh=True
    )

    print(f"Indexed document to {index}: {doc_id}, result: {response.get('result')}")


def create_index(client, index: str) -> None:
    """
    Create OpenSearch index.

    The index template (job-events-template) provides mappings automatically.
    This function just creates the index - settings and mappings come from template.

    Args:
        client: OpenSearch client
        index: Index name to create
    """
    # Just create the index - template provides settings and mappings
    response = client.indices.create(index=index)
    print(f"Created index: {index}, response: {response}")
