"""
Tests for SimpleETLJob
======================

Demonstrates testing SparkRouter jobs.
"""

import pytest

from examples.simple_etl.simple_job import SimpleETLJob
from examples.simple_etl.simple_job_factory import SimpleETLJobFactory


class TestSimpleETLJob:
    """Tests for SimpleETLJob."""

    def test_execute_job_returns_metrics(self):
        """Job should return processing metrics."""
        job = SimpleETLJob()

        result = job.run(
            input_path="/input",
            output_path="/output",
        )

        assert "records_processed" in result
        assert "records_written" in result

    def test_execute_job_with_custom_filter(self):
        """Job should accept custom filter parameters."""
        job = SimpleETLJob()

        result = job.run(
            input_path="/input",
            output_path="/output",
            filter_column="type",
            filter_value="premium",
        )

        assert result["records_processed"] == 1000


class TestSimpleETLJobFactory:
    """Tests for SimpleETLJobFactory."""

    def test_create_job(self):
        """Factory should create job instance."""
        factory = SimpleETLJobFactory()

        job = factory.create_job()

        assert isinstance(job, SimpleETLJob)

    def test_run_executes_job(self):
        """Factory.run() should create and execute job."""
        factory = SimpleETLJobFactory()

        result = factory.run(
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
            input_path="/input",
            output_path="/output",
            service_provider="CONTAINER",
            has_spark=True,
        )

        assert result["records_processed"] == 1000
