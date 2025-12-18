"""
Tests for SimpleETLJob
======================

Demonstrates testing jobs without mocks using Noop implementations.
"""

import pytest

from sparkrouter.testing.noop import NoopNotificationService

from examples.simple_etl.simple_job import SimpleETLJob
from examples.simple_etl.simple_job_factory import SimpleETLJobFactory


class TestSimpleETLJob:
    """Tests for SimpleETLJob using Noop implementations."""

    def test_execute_job_returns_metrics(self):
        """Job should return processing metrics."""
        notifier = NoopNotificationService()
        job = SimpleETLJob(notification_service=notifier)

        result = job.run(
            input_path="/input",
            output_path="/output",
        )

        assert "records_processed" in result
        assert "records_written" in result

    def test_on_success_sends_notification(self):
        """Success should trigger notification."""
        notifier = NoopNotificationService()
        job = SimpleETLJob(notification_service=notifier)

        job.run(
            input_path="/input",
            output_path="/output",
        )

        assert len(notifier.notifications) == 1
        assert "Success" in notifier.notifications[0]["subject"]

    def test_on_failure_sends_notification(self):
        """Failure should trigger notification."""
        notifier = NoopNotificationService()

        # Create a job that will fail
        class FailingJob(SimpleETLJob):
            def execute_job(self, **kwargs):
                raise ValueError("Test failure")

        job = FailingJob(notification_service=notifier)

        with pytest.raises(RuntimeError):
            job.run(input_path="/input", output_path="/output")

        assert len(notifier.notifications) == 1
        assert "FAILED" in notifier.notifications[0]["subject"]


class TestSimpleETLJobFactory:
    """Tests for SimpleETLJobFactory."""

    def test_create_job_with_noop_notification(self):
        """Factory should create job with noop notification service."""
        factory = SimpleETLJobFactory()

        job = factory.create_job(
            simple_etl_job={"notification": {"type": "noop"}}
        )

        assert isinstance(job, SimpleETLJob)

    def test_run_executes_job(self):
        """Factory.run() should create and execute job."""
        factory = SimpleETLJobFactory()

        result = factory.run(
            simple_etl_job='{"notification": {"type": "noop"}}',
            input_path="/input",
            output_path="/output",
        )

        assert result["records_processed"] == 1000

    def test_factory_filters_extra_kwargs(self):
        """Factory should filter kwargs not in execute_job signature."""
        factory = SimpleETLJobFactory()

        # service_provider and has_spark are added by entry points
        # but not used by execute_job - they should be filtered out
        result = factory.run(
            simple_etl_job={"notification": {"type": "noop"}},
            input_path="/input",
            output_path="/output",
            service_provider="CONTAINER",
            has_spark=True,
        )

        assert result["records_processed"] == 1000
