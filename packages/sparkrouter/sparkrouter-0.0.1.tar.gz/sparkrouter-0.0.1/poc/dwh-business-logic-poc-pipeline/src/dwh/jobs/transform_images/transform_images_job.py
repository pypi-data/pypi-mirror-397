from datetime import datetime
from typing import Any

from dwh.jobs.abstract_job import AbstractJob
from dwh.jobs.load_promos.job_utils import JobUtils
from dwh.jobs.transform_images.extract.image_extractor import ImageExtractor
from dwh.jobs.transform_images.load.image_loader import ImageLoader
from dwh.jobs.transform_images.load.dropped_record_loader import DroppedRecordLoader
from dwh.jobs.transform_images.transform.image_transformer import ImageTransformer
from dwh.jobs.transform_images.metrics.job_metrics import JobMetrics
from dwh.services.quality.quality_checker import QualityChecker
from dwh.services.quality.quality_models import QualityResult, QualityCheckFailedError
from dwh.services.event.job_event_publisher import JobEventPublisher


class TransformImagesJob(AbstractJob):
    """
    Transform images job with optional quality checking and event publishing.

    Quality checks and event publishing are optional - if not provided, the job
    runs without them (backward compatible with simple notification services).

    Alert evaluation and sending is handled by downstream lambdas that subscribe
    to the job_events topic - not by the job itself.
    """

    def __init__(
            self,
            image_extractor: ImageExtractor,
            image_transformer: ImageTransformer,
            image_loader: ImageLoader,
            dropped_record_loader: DroppedRecordLoader = None,
            # Optional: Quality checking
            quality_checker: QualityChecker = None,
            # Optional: Event publishing
            event_publisher: JobEventPublisher = None,
    ):
        self.extract = image_extractor
        self.image_transformer = image_transformer
        self.image_loader = image_loader
        self.dropped_record_loader = dropped_record_loader

        # Optional quality/event services
        self.quality_checker = quality_checker
        self.event_publisher = event_publisher

        # Store last metrics for use in on_success/on_failure
        self._last_metrics: dict = {}
        self._last_quality: QualityResult = None

    def execute_job(self, start_date: str, end_date: str, created_by: str, clean_sink: bool = True, **kwargs) -> Any:
        # Initialize metrics collection
        metrics = JobMetrics()

        # Capture execution context
        metrics.start_date = start_date
        metrics.end_date = end_date
        metrics.created_by = created_by
        metrics.service_provider = kwargs.get('service_provider', None)
        metrics.environment = kwargs.get('environment', None)
        metrics.region = kwargs.get('region', None)

        # Capture data paths
        metrics.source_base_path = self.extract.s3_data_source.base_path if hasattr(self.extract.s3_data_source, 'base_path') else None
        # Capture all sink base paths (multiple sinks for different categories)
        if hasattr(self.image_loader, 'data_sinks'):
            metrics.sink_base_paths = {cat: sink.base_path for cat, sink in self.image_loader.data_sinks.items()}
            # For backward compatibility, use first sink's base path as primary
            metrics.sink_base_path = next(iter(self.image_loader.data_sinks.values())).base_path
        else:
            metrics.sink_base_path = None
            metrics.sink_base_paths = {}

        # tellme: are these dates always in utc?
        start_date_utc: datetime = JobUtils.parse_date_to_datetime(start_date, "start_date")
        end_date_utc: datetime = JobUtils.parse_date_to_datetime(end_date, "end_date")

        if not created_by:
            raise ValueError("created_by parameter is required")

        # Extract Phase: read images from S3
        print("Extraction: Starting ...")
        extract_start = datetime.utcnow()
        metrics.extract_start_time = extract_start
        raw_df, extract_dropped_df = self.extract.extract(start_date_utc, end_date_utc, metrics)
        extract_end = datetime.utcnow()
        metrics.extract_end_time = extract_end
        metrics.extract_duration_seconds = (extract_end - extract_start).total_seconds()
        print("Extraction: Completed.")

        # Transform Phase: decrypt/decode image records
        print("Transform: Starting ...")
        transform_start = datetime.utcnow()
        metrics.transform_start_time = transform_start
        transformed_df, transform_dropped_df = self.image_transformer.transform(raw_df, created_by, metrics)
        transform_end = datetime.utcnow()
        metrics.transform_end_time = transform_end
        metrics.transform_duration_seconds = (transform_end - transform_start).total_seconds()
        print("Transform: Completed.")

        # Load Phase: serialize to S3
        print("Load: Starting ...")
        load_start = datetime.utcnow()
        metrics.load_start_time = load_start
        self.image_loader.load(transformed_df, metrics, clean_sink=clean_sink)
        load_end = datetime.utcnow()
        metrics.load_end_time = load_end
        metrics.load_duration_seconds = (load_end - load_start).total_seconds()
        print("Load: Complete")

        # Load Dropped Records: serialize dropped records to S3 for analysis
        if self.dropped_record_loader:
            print("Dropped Records Load: Starting ...")
            dropped_dfs = [extract_dropped_df, transform_dropped_df]
            self.dropped_record_loader.load(dropped_dfs, metrics)
            print("Dropped Records Load: Complete")
        else:
            print("Dropped Records Load: Skipped (no loader configured)")

        # Capture resource utilization metrics
        self._capture_resource_metrics(metrics)

        # Finalize metrics and print summary
        metrics.job_status = "SUCCESS"
        metrics.complete()
        print(metrics.get_summary())

        # Store metrics for event publishing
        self._last_metrics = metrics.get_json()

        # Run quality checks if configured
        if self.quality_checker:
            quality_metrics = {
                "records_read": self._last_metrics.get("records_read", 0),
                "records_written": self._last_metrics.get("records_written", 0),
                "records_dropped": self._last_metrics.get("records_dropped", 0),
                "bytes_written": self._last_metrics.get("bytes_written", 0),
            }
            self._last_quality = self.quality_checker.check(quality_metrics)
            print(f"Quality check result: {self._last_quality.status}")

            # If quality is RED, raise error (will trigger on_failure)
            if self._last_quality.status == "RED":
                raise QualityCheckFailedError(self._last_quality)
        else:
            self._last_quality = QualityResult.green()

        return self._last_metrics

    def on_success(self, results) -> None:
        """Handle successful job execution - publish event."""
        self._publish_job_event(error=None)

    def on_failure(self, error_message: str) -> None:
        """Handle job failure - publish event."""
        error = RuntimeError(error_message)
        self._publish_job_event(error=error)

    def _publish_job_event(self, error: Exception = None) -> None:
        """Publish job event. Alert evaluation is handled by downstream lambdas."""
        if not self.event_publisher:
            return

        job_run_id = self._last_metrics.get("job_run_id", "unknown")
        quality = self._last_quality or QualityResult.green()

        self.event_publisher.publish(
            job_name="transform_images",
            job_run_id=job_run_id,
            metrics=self._last_metrics,
            quality=quality,
            error=error
        )

    def _capture_resource_metrics(self, metrics: JobMetrics) -> None:
        """Capture Spark/Glue resource utilization metrics if available"""
        try:
            # Try to get SparkContext from the extractor's data source
            # ImageExtractor has s3_data_source (SparkS3DataSource), which has spark
            spark = self.extract.s3_data_source.spark
            sc = spark.sparkContext

            # Capture job run ID (Spark application ID - universal across platforms)
            metrics.job_run_id = sc.applicationId

            # Get executor configuration
            conf = sc.getConf()

            # Extract executor count (from active executors)
            try:
                metrics.spark_executor_count = len(sc._jsc.sc().statusTracker().getExecutorInfos()) - 1  # Exclude driver
            except:
                pass

            # Extract memory configuration
            try:
                executor_memory_str = conf.get("spark.executor.memory", "0g")
                metrics.spark_executor_memory_gb = self._parse_memory_to_gb(executor_memory_str)
            except:
                pass

            try:
                driver_memory_str = conf.get("spark.driver.memory", "0g")
                metrics.spark_driver_memory_gb = self._parse_memory_to_gb(driver_memory_str)
            except:
                pass

            # Calculate Glue DPU-seconds if running on Glue
            # DPU = (executor_count * executor_memory_gb / 16) + driver overhead
            # This is an approximation - actual billing from Glue CloudWatch is more accurate
            if metrics.spark_executor_count > 0 and metrics.spark_executor_memory_gb > 0:
                total_duration = metrics.get_duration_seconds()
                executor_dpus = (metrics.spark_executor_count * metrics.spark_executor_memory_gb) / 16
                # Add 1 DPU for driver
                total_dpus = executor_dpus + 1
                metrics.glue_dpu_seconds = total_dpus * total_duration

        except Exception as e:
            # Resource metrics are optional - don't fail the job if unavailable
            print(f"INFO: Could not capture resource metrics: {e}")

    @staticmethod
    def _parse_memory_to_gb(memory_str: str) -> int:
        """Parse Spark memory string (e.g., '16g', '4096m') to GB integer"""
        memory_str = memory_str.lower().strip()
        if memory_str.endswith('g'):
            return int(memory_str[:-1])
        elif memory_str.endswith('m'):
            return int(memory_str[:-1]) // 1024
        elif memory_str.endswith('k'):
            return int(memory_str[:-1]) // (1024 * 1024)
        else:
            return int(memory_str) // (1024 * 1024 * 1024)
