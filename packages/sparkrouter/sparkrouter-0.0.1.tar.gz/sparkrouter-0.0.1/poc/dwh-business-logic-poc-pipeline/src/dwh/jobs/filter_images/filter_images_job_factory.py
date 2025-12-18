"""
Factory for creating FilterImagesJob instances.

Parses configuration and wires up all dependencies.
"""
import logging
from datetime import datetime, timezone
from typing import List

from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.filter_images.filter_images_job import FilterImagesJob
from dwh.jobs.filter_images.extract.transform_output_reader import TransformOutputReader
from dwh.jobs.filter_images.extract.filtered_output_reader import FilteredOutputReader
from dwh.jobs.filter_images.transform.filter_transformer import FilterTransformer
from dwh.jobs.filter_images.load.filter_loader import FilterLoader
from dwh.jobs.filter_images.manifest.manifest_service import SparkManifestService
from dwh.services.spark.spark_session_factory import SparkSessionFactory
from dwh.services.event.job_event_publisher_factory import JobEventPublisherFactory

logger = logging.getLogger(__name__)


class FilterImagesJobFactory(AbstractJobFactory):
    """
    Factory for FilterImagesJob.

    Configuration structure:
    {
        "base_path": "s3://bucket/filtered_images",
        "timezone": "America/Los_Angeles",
        "transform_output_path": "s3://bucket/transformed/...",
        "triggered_by_job": "transform_images",
        "triggered_by_run_id": "spark-xxx",
        "dedup_key_columns": ["mediaid"],
        "dedup_order_column": "updated",
        "time_column": "updated",
        "max_records_per_file": 500000,
        "event_publisher_config": {"publisher_type": "SNS", ...}
    }
    """

    def __init__(
        self,
        spark_factory=None,
        **kwargs
    ):
        """Initialize with optional factory dependencies."""
        super().__init__(**kwargs)
        self.spark_factory = spark_factory or SparkSessionFactory

    def _get_spark_session(self, **kwargs):
        """Create a Spark session if has_spark is True."""
        has_spark = kwargs.get('has_spark', False)
        if isinstance(has_spark, str):
            has_spark = has_spark.lower() in ['true', '1', 'yes']

        if has_spark:
            return self.spark_factory.create_spark_session(**kwargs)

        return None

    def create_job(self, **kwargs) -> FilterImagesJob:
        """
        Create a FilterImagesJob instance.

        Args:
            **kwargs: Configuration parameters

        Returns:
            Configured FilterImagesJob
        """
        config = self.parse_job_config(job_name='filter_images_job', **kwargs)
        print(f"Configuration for FilterImagesJob: {config}")

        # Get Spark session
        spark = self._get_spark_session(**kwargs)
        if spark is None:
            raise ValueError('filter_images_job requires a spark_session')
        print(f"Spark session created: {spark is not None}")

        # Extract configuration
        base_path = config['base_path']
        timezone_name = config.get('timezone', 'America/Los_Angeles')
        dedup_key_columns = config.get('dedup_key_columns', ['mediaid'])
        dedup_order_column = config.get('dedup_order_column', 'updated')
        time_column = config.get('time_column', 'updated')
        max_records_per_file = config.get('max_records_per_file', 500000)

        # Create readers
        transform_output_reader = TransformOutputReader(spark)
        filtered_output_reader = FilteredOutputReader(spark)

        # Create transformer
        transformer = FilterTransformer(
            dedup_key_columns=dedup_key_columns,
            dedup_order_column=dedup_order_column
        )

        # Create loader
        loader = FilterLoader(
            spark=spark,
            max_records_per_file=max_records_per_file
        )

        # Create manifest service
        manifest_service = SparkManifestService(spark)

        # Create event publisher
        event_publisher_config = config.get('event_publisher_config', {'publisher_type': 'NOOP'})
        event_publisher = JobEventPublisherFactory.create_job_event_publisher(event_publisher_config)

        # Create job
        return FilterImagesJob(
            transform_output_reader=transform_output_reader,
            filtered_output_reader=filtered_output_reader,
            transformer=transformer,
            loader=loader,
            manifest_service=manifest_service,
            base_path=base_path,
            timezone_name=timezone_name,
            time_column=time_column,
            event_publisher=event_publisher,
        )

    def run(self, **kwargs):
        """
        Run the filter_images job.

        Expected kwargs:
            - filter_images_job: Job configuration JSON
            - transform_output_path: Path to transform_images output
            - triggered_by_job: Name of triggering job
            - triggered_by_run_id: Run ID of triggering job
            - start_date/end_date: Optional date range (used to derive year/month/day)
        """
        config = self.parse_job_config(job_name='filter_images_job', **kwargs)

        # Get trigger info from config or kwargs
        transform_output_path = config.get('transform_output_path') or kwargs.get('transform_output_path')
        triggered_by_job = config.get('triggered_by_job') or kwargs.get('triggered_by_job', 'unknown')
        triggered_by_run_id = config.get('triggered_by_run_id') or kwargs.get('triggered_by_run_id', 'unknown')

        if not transform_output_path:
            raise ValueError("transform_output_path is required")

        # Determine date (year, month, day)
        # Use end_date if provided, otherwise use current date in configured timezone
        timezone_name = config.get('timezone', 'America/Los_Angeles')
        year, month, day = self._get_date_components(kwargs, timezone_name)

        # Create and run job
        job = self.create_job(**kwargs)

        return job.run(
            transform_output_path=transform_output_path,
            triggered_by_job=triggered_by_job,
            triggered_by_run_id=triggered_by_run_id,
            year=year,
            month=month,
            day=day,
            service_provider=kwargs.get('service_provider'),
            environment=kwargs.get('environment'),
            region=kwargs.get('region'),
            created_by=kwargs.get('created_by'),
        )

    def _get_date_components(self, kwargs: dict, timezone_name: str) -> tuple:
        """
        Get year, month, day from kwargs or current time.

        Args:
            kwargs: Job arguments
            timezone_name: Timezone for current time fallback

        Returns:
            Tuple of (year, month, day)
        """
        # Try to get from explicit parameters
        if 'year' in kwargs and 'month' in kwargs and 'day' in kwargs:
            return int(kwargs['year']), int(kwargs['month']), int(kwargs['day'])

        # Try to parse from end_date
        end_date = kwargs.get('end_date')
        if end_date:
            try:
                dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                return dt.year, dt.month, dt.day
            except (ValueError, AttributeError):
                pass

        # Fall back to current date in timezone
        # Note: For production, should use proper timezone conversion
        now = datetime.now(timezone.utc)
        return now.year, now.month, now.day


def main(**kwargs):
    """
    Entrypoint for FilterImages job.

    Called by generic_entry.py when running:
        --module_name dwh.jobs.filter_images.filter_images_job_factory
    """
    print(f"filter_images_job_factory kwargs: {kwargs}")

    factory = FilterImagesJobFactory(**kwargs)
    return factory.run(**kwargs)
