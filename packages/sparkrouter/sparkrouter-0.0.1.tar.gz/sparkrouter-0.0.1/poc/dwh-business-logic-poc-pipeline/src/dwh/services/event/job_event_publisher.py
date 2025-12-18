import json
import traceback
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from dwh.services.quality.quality_models import QualityResult, QualityCheckFailedError


class JobEventPublisher(ABC):
    """
    Abstract base class for publishing job events.

    Publishes to job_events topic with complete job context.
    """

    @abstractmethod
    def publish(
        self,
        job_name: str,
        job_run_id: str,
        metrics: dict,
        quality: QualityResult,
        error: Exception = None
    ) -> dict:
        """
        Publish a job completion event.

        Args:
            job_name: Name of the job
            job_run_id: Unique identifier for this job run
            metrics: Job metrics dictionary
            quality: Quality check results
            error: Exception if job failed, None otherwise

        Returns:
            The event dictionary that was published
        """
        raise NotImplementedError

    def _build_event(
        self,
        job_name: str,
        job_run_id: str,
        metrics: dict,
        quality: QualityResult,
        error: Exception = None
    ) -> dict:
        """Build the job event dictionary."""
        status = self._determine_status(quality, error)
        failure_type = self._determine_failure_type(quality, error)

        event = {
            "event_type": "job_completed",
            "job_name": job_name,
            "job_run_id": job_run_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",

            "status": status,
            "failure_type": failure_type,

            "artifacts_available": status != "FAILED",
            "artifacts": self._extract_artifacts(metrics),

            "quality": quality.to_dict(),

            # Pass through the full metrics dict - don't filter
            "metrics": metrics,

            "error": self._build_error_dict(error) if error else None
        }

        return event

    def _determine_status(self, quality: QualityResult, error: Exception) -> str:
        """
        Determine job status based on quality and error.

        Returns:
            SUCCESS - Quality GREEN or YELLOW, no error
            PENDING_APPROVAL - Quality RED, artifacts exist
            FAILED - Catastrophic error (not quality-related)
        """
        # Catastrophic failure (non-quality exception)
        if error and not isinstance(error, QualityCheckFailedError):
            return "FAILED"

        # Quality RED = pending approval (artifacts exist)
        if quality.status == "RED":
            return "PENDING_APPROVAL"

        # Quality GREEN or YELLOW = success
        return "SUCCESS"

    def _determine_failure_type(self, quality: QualityResult, error: Exception) -> str | None:
        """Determine the type of failure if any."""
        if error and not isinstance(error, QualityCheckFailedError):
            return "CATASTROPHIC"
        if quality.status == "RED":
            return "QUALITY"
        return None

    def _extract_artifacts(self, metrics: dict) -> dict:
        """Extract artifact information from metrics."""
        artifacts = {}

        # Extract from load output summary if available
        output_summary = metrics.get("load_output_summary", {})
        for category, summary in output_summary.items():
            if category == "dropped":
                continue  # Don't include dropped records as artifacts
            artifacts[category] = {
                "path": summary.get("base_path", ""),
                "records": summary.get("records", 0),
                "bytes": summary.get("bytes", 0)
            }

        return artifacts

    def _build_error_dict(self, error: Exception) -> dict:
        """Build error dictionary from exception."""
        return {
            "type": type(error).__name__,
            "message": str(error),
            "stack_trace": traceback.format_exc()
        }


class SNSJobEventPublisher(JobEventPublisher):
    """Publishes job events to SNS topic."""

    def __init__(self, region: str, topic_arn: str):
        import boto3
        self.topic_arn = topic_arn
        self.region = region
        self.sns_client = boto3.client('sns', region_name=region)
        print(f"SNSJobEventPublisher initialized with topic_arn={topic_arn}, region={region}")

    def publish(
        self,
        job_name: str,
        job_run_id: str,
        metrics: dict,
        quality: QualityResult,
        error: Exception = None
    ) -> dict:
        """Publish job event to SNS."""
        event = self._build_event(job_name, job_run_id, metrics, quality, error)

        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=json.dumps(event),
                Subject=f"Job Event: {job_name} - {event['status']}",
                MessageAttributes={
                    "status": {
                        "DataType": "String",
                        "StringValue": event["status"]
                    },
                    "job_name": {
                        "DataType": "String",
                        "StringValue": job_name
                    }
                }
            )
            print(f"Published job event to {self.topic_arn}: {response.get('MessageId')}")
        except Exception as e:
            print(f"Failed to publish job event to topic_arn={self.topic_arn}, region={self.region}: {e}")
            raise

        return event


class NoopJobEventPublisher(JobEventPublisher):
    """No-op publisher for testing. Captures events without sending."""

    def __init__(self):
        self.published_events: list[dict] = []

    def publish(
        self,
        job_name: str,
        job_run_id: str,
        metrics: dict,
        quality: QualityResult,
        error: Exception = None
    ) -> dict:
        """Capture event without publishing."""
        event = self._build_event(job_name, job_run_id, metrics, quality, error)
        self.published_events.append(event)
        print(f"[NoopJobEventPublisher] Captured event: {job_name} - {event['status']}")
        return event
