"""
Service for publishing job metrics to AWS EventBridge for OpenSearch indexing.

This service allows jobs to publish their performance metrics to EventBridge,
which triggers a Lambda function that indexes the data into OpenSearch for
real-time monitoring and dashboards.

Usage:
    from dwh.services.metrics_publisher import MetricsPublisher

    publisher = MetricsPublisher(region='us-west-1')
    publisher.publish_metrics(
        job_name='transform_images',
        job_run_id='jr_abc123',
        metrics=metrics_dict
    )
"""

import boto3
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime


logger = logging.getLogger(__name__)


class MetricsPublisher:
    """
    Publishes job metrics to AWS EventBridge for downstream processing.

    The published metrics are captured by EventBridge rules and processed by
    a Lambda function that indexes them into OpenSearch for monitoring.
    """

    def __init__(self, region: str = 'us-west-1', enabled: bool = True):
        """
        Initialize metrics publisher.

        Args:
            region: AWS region for EventBridge
            enabled: Whether publishing is enabled (set to False to disable)
        """
        self.region = region
        self.enabled = enabled
        self.events_client = None

        if self.enabled:
            try:
                self.events_client = boto3.client('events', region_name=region)
                logger.info(f"MetricsPublisher initialized for region {region}")
            except Exception as e:
                logger.error(f"Failed to initialize EventBridge client: {e}")
                self.enabled = False

    def publish_metrics(
        self,
        job_name: str,
        job_run_id: str,
        metrics: Dict[str, Any],
        source: str = 'dwh.pipeline'
    ) -> bool:
        """
        Publish job metrics to EventBridge.

        Args:
            job_name: Name of the job (e.g., 'transform_images')
            job_run_id: Unique identifier for this job run
            metrics: Dictionary containing job metrics (will be JSON serialized)
            source: EventBridge event source (default: 'dwh.pipeline')

        Returns:
            True if published successfully, False otherwise
        """
        if not self.enabled:
            logger.warning("MetricsPublisher is disabled, skipping metrics publication")
            return False

        if not self.events_client:
            logger.error("EventBridge client not initialized")
            return False

        try:
            # Prepare event detail
            detail = {
                'job_name': job_name,
                'job_run_id': job_run_id,
                'metrics': metrics,
                'published_at': datetime.utcnow().isoformat()
            }

            # Publish to EventBridge
            response = self.events_client.put_events(
                Entries=[
                    {
                        'Source': source,
                        'DetailType': 'Job Metrics',
                        'Detail': json.dumps(detail, default=str),
                        'Time': datetime.utcnow()
                    }
                ]
            )

            # Check for failures
            if response.get('FailedEntryCount', 0) > 0:
                logger.error(f"Failed to publish metrics: {response.get('Entries')}")
                return False

            logger.info(f"Successfully published metrics for {job_name} (run: {job_run_id})")
            return True

        except Exception as e:
            logger.error(f"Error publishing metrics to EventBridge: {e}")
            return False

    def publish_job_completion(
        self,
        job_name: str,
        job_run_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Publish job completion event with status and optional metrics.

        Args:
            job_name: Name of the job
            job_run_id: Unique identifier for this job run
            status: Job status ('SUCCESS', 'FAILED', 'TIMEOUT', etc.)
            metrics: Optional detailed metrics dictionary
            error_message: Optional error message if job failed

        Returns:
            True if published successfully, False otherwise
        """
        detail = {
            'job_name': job_name,
            'job_run_id': job_run_id,
            'status': status,
            'completed_at': datetime.utcnow().isoformat()
        }

        if metrics:
            detail['metrics'] = metrics

        if error_message:
            detail['error_message'] = error_message

        if not self.enabled or not self.events_client:
            logger.warning("MetricsPublisher is disabled, skipping completion event")
            return False

        try:
            response = self.events_client.put_events(
                Entries=[
                    {
                        'Source': 'dwh.pipeline',
                        'DetailType': 'Job Completion',
                        'Detail': json.dumps(detail, default=str),
                        'Time': datetime.utcnow()
                    }
                ]
            )

            if response.get('FailedEntryCount', 0) > 0:
                logger.error(f"Failed to publish completion event: {response.get('Entries')}")
                return False

            logger.info(f"Published completion event for {job_name}: {status}")
            return True

        except Exception as e:
            logger.error(f"Error publishing completion event: {e}")
            return False


class NoOpMetricsPublisher(MetricsPublisher):
    """
    No-op metrics publisher for testing and development.

    This implementation logs metrics without actually publishing to EventBridge,
    useful for local testing and unit tests.
    """

    def __init__(self, **kwargs):
        """Initialize no-op publisher (ignores all kwargs)."""
        self.enabled = True
        self.events_client = None
        logger.info("NoOpMetricsPublisher initialized (metrics will be logged only)")

    def publish_metrics(
        self,
        job_name: str,
        job_run_id: str,
        metrics: Dict[str, Any],
        source: str = 'dwh.pipeline'
    ) -> bool:
        """Log metrics instead of publishing."""
        logger.info(
            f"[NoOp] Would publish metrics for {job_name} (run: {job_run_id}): "
            f"{json.dumps(metrics, indent=2, default=str)}"
        )
        return True

    def publish_job_completion(
        self,
        job_name: str,
        job_run_id: str,
        status: str,
        metrics: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Log completion event instead of publishing."""
        logger.info(
            f"[NoOp] Would publish completion for {job_name}: {status}"
        )
        return True


# Factory function for creating publisher
def create_metrics_publisher(
    region: str = 'us-west-1',
    enabled: bool = True,
    use_noop: bool = False
) -> MetricsPublisher:
    """
    Factory function to create appropriate metrics publisher.

    Args:
        region: AWS region
        enabled: Whether publishing is enabled
        use_noop: If True, return NoOpMetricsPublisher for testing

    Returns:
        MetricsPublisher instance
    """
    if use_noop:
        return NoOpMetricsPublisher()
    else:
        return MetricsPublisher(region=region, enabled=enabled)
