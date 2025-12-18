import pytest
from pathlib import Path
from typing import Optional, List
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType, StructField, StringType

from dwh.jobs.filter_images.filter_images_job import FilterImagesJob
from dwh.jobs.filter_images.extract.transform_output_reader import TransformOutputReader
from dwh.jobs.filter_images.extract.filtered_output_reader import FilteredOutputReader
from dwh.jobs.filter_images.transform.filter_transformer import FilterTransformer
from dwh.jobs.filter_images.load.filter_loader import FilterLoader
from dwh.jobs.filter_images.manifest.manifest_service import ManifestService
from dwh.jobs.filter_images.manifest.manifest_models import FilterManifest
from dwh.jobs.filter_images.metrics.job_metrics import FilterImagesJobMetrics
from dwh.jobs.transform_images.load.image_loader import ImageLoader

from dwh.services.quality.quality_checker import NoopQualityChecker
from dwh.services.event.job_event_publisher import NoopJobEventPublisher

pytestmark = pytest.mark.functional


class TestFilterImagesJobEndToEnd:
    """
    End-to-end functional tests for FilterImagesJob.

    Tests the complete pipeline: previous filtered + new transform → job execution → final output.
    Only file I/O is stubbed - all business logic runs for real.
    """

    def test_filter_images_job_with_previous_data(self, spark_session: SparkSession):
        """
        Test combining previous filtered output with new transform output.

        Validates:
        1. Unique records from previous data are kept
        2. Unique records from new data are added
        3. Duplicate records (same mediaid) use LAST (newer source) version
        4. Metrics correctly track deduplication
        """
        # 1. Load test data
        test_data_dir = Path(__file__).parent
        schema = self._get_schema_with_source_timestamp()

        previous_df = (
            spark_session.read
            .schema(schema)
            .json(str(test_data_dir / "previous_filtered.jsonl"))
        )
        new_df = (
            spark_session.read
            .schema(ImageLoader.get_output_schema())
            .json(str(test_data_dir / "new_transform.jsonl"))
        )
        expected_df = (
            spark_session.read
            .schema(ImageLoader.get_output_schema())
            .json(str(test_data_dir / "expected_output.jsonl"))
        )

        # 2. Setup stubbed infrastructure
        fake_transform_reader = FakeTransformOutputReader(spark_session, test_df=new_df)
        fake_filtered_reader = FakeFilteredOutputReader(spark_session, test_df=previous_df)
        fake_loader = FakeFilterLoader(spark=spark_session)
        fake_manifest_service = FakeManifestService(
            previous_manifest=FilterManifest(
                run_id="filter-20250115T080000Z-abc123",
                status="SUCCESS",
                output_path="s3://test/filtered_images/pacific/year=2025/month=01/day=15/filter-20250115T080000Z-abc123"
            )
        )

        # 3. Create REAL business logic components
        transformer = FilterTransformer(
            dedup_key_columns=["data.mediaid"],
            dedup_order_column="eventTime"
        )

        # 4. Instantiate and run the job
        job = FilterImagesJob(
            transform_output_reader=fake_transform_reader,
            filtered_output_reader=fake_filtered_reader,
            transformer=transformer,
            loader=fake_loader,
            manifest_service=fake_manifest_service,
            base_path="s3://test/filtered_images",
            timezone_name="America/Los_Angeles",
            time_column="eventTime",
            event_publisher=NoopJobEventPublisher(),
            quality_checker=NoopQualityChecker()
        )

        result = job.execute_job(
            transform_output_path="s3://test/transformed_images/nautilus/2025/01/15",
            triggered_by_job="transform_images",
            triggered_by_run_id="transform-20250115T100000Z-xyz789",
            year=2025,
            month=1,
            day=15
        )

        # 5. Validate results
        actual_df = fake_loader.get_written_data()
        self._validate_output(actual_df, expected_df)

        # 6. Validate metrics
        assert result["records_written"] == 4, "Should have 4 records after deduplication"
        assert result["payload"]["deduplication"]["duplicates_removed"] == 2, \
            "Should remove 2 duplicates (media-001 and media-002)"
        assert result["payload"]["deduplication"]["records_before_dedup"] == 6, \
            "Should have 6 records before dedup (3 previous + 3 new)"

        print("Test PASSED: Deduplication with previous data works correctly")

    def test_filter_images_job_first_run(self, spark_session: SparkSession):
        """
        Test first run of the day (no previous data).

        Validates:
        1. Job completes successfully without previous data
        2. All new records are written
        3. No deduplication occurs (no duplicates to remove)
        4. Metrics correctly reflect first-run scenario
        """
        # 1. Load test data
        test_data_dir = Path(__file__).parent
        new_df = (
            spark_session.read
            .schema(ImageLoader.get_output_schema())
            .json(str(test_data_dir / "first_run_transform.jsonl"))
        )

        # 2. Setup stubbed infrastructure (no previous data)
        fake_transform_reader = FakeTransformOutputReader(spark_session, test_df=new_df)
        fake_filtered_reader = FakeFilteredOutputReader(spark_session, test_df=None)
        fake_loader = FakeFilterLoader(spark=spark_session)
        fake_manifest_service = FakeManifestService(previous_manifest=None)

        # 3. Create REAL business logic components
        transformer = FilterTransformer(
            dedup_key_columns=["data.mediaid"],
            dedup_order_column="eventTime"
        )

        # 4. Instantiate and run the job
        job = FilterImagesJob(
            transform_output_reader=fake_transform_reader,
            filtered_output_reader=fake_filtered_reader,
            transformer=transformer,
            loader=fake_loader,
            manifest_service=fake_manifest_service,
            base_path="s3://test/filtered_images",
            timezone_name="America/Los_Angeles",
            time_column="eventTime",
            event_publisher=NoopJobEventPublisher(),
            quality_checker=NoopQualityChecker()
        )

        result = job.execute_job(
            transform_output_path="s3://test/transformed_images/nautilus/2025/01/15",
            triggered_by_job="transform_images",
            triggered_by_run_id="transform-20250115T090000Z-first",
            year=2025,
            month=1,
            day=15
        )

        # 5. Validate results
        actual_df = fake_loader.get_written_data()
        assert actual_df is not None, "Data should be written"
        assert actual_df.count() == 2, "Should have 2 records from first run"

        # 6. Validate metrics
        assert result["records_written"] == 2, "Should write all 2 records"
        assert result["payload"]["deduplication"]["duplicates_removed"] == 0, \
            "Should remove 0 duplicates (first run)"

        print("Test PASSED: First run (no previous data) works correctly")

    def test_filter_images_job_no_new_data(self, spark_session: SparkSession):
        """
        Test behavior when new transform output is empty.

        Validates:
        1. Job raises error (new data is required)
        """
        # Setup stubbed infrastructure with empty transform reader
        fake_transform_reader = FakeTransformOutputReader(spark_session, test_df=None, raise_on_read=True)
        fake_filtered_reader = FakeFilteredOutputReader(spark_session, test_df=None)
        fake_loader = FakeFilterLoader(spark=spark_session)
        fake_manifest_service = FakeManifestService(previous_manifest=None)

        transformer = FilterTransformer(
            dedup_key_columns=["data.mediaid"],
            dedup_order_column="eventTime"
        )

        job = FilterImagesJob(
            transform_output_reader=fake_transform_reader,
            filtered_output_reader=fake_filtered_reader,
            transformer=transformer,
            loader=fake_loader,
            manifest_service=fake_manifest_service,
            base_path="s3://test/filtered_images",
            timezone_name="America/Los_Angeles",
            time_column="eventTime",
            event_publisher=NoopJobEventPublisher()
        )

        # Should raise error when no new data is found
        with pytest.raises(ValueError, match="No data found at transform output path"):
            job.execute_job(
                transform_output_path="s3://test/empty",
                triggered_by_job="transform_images",
                triggered_by_run_id="transform-empty",
                year=2025,
                month=1,
                day=15
            )

        print("Test PASSED: Empty new data raises appropriate error")

    def test_last_duplicate_wins_strategy(self, spark_session: SparkSession):
        """
        Test that the last-duplicate-wins strategy always keeps the newer record.

        Creates data where:
        - Previous has record A with old timestamp
        - New has record A with newer timestamp
        - Result should have record A from new data (newer wins)
        """
        # Create test data with explicit timestamps
        schema = self._get_schema_with_source_timestamp()

        # Previous record with older source timestamp
        previous_data = [
            {
                "eventTime": "2025-01-15T08:00:00.000000",
                "event_time": "2025-01-15T08:00:00.000000",
                "pk": "proj-X_user-X",
                "data": {
                    "projectguid": "proj-X",
                    "project_type": "PHOTOBOOK",
                    "project_subtype": "STANDARD",
                    "userid": "user-X",
                    "inserted": "2025-01-15T07:00:00.000000",
                    "updated": "2025-01-15T08:00:00.000000",
                    "product_index": 1,
                    "product_type": "BOOK",
                    "productguid": "product-X",
                    "productimageid": "img-OLD",
                    "msp": "MSP1",
                    "mspid": "mspid-X",
                    "mediaid": "same-media-id",
                    "locationspec": "loc-OLD"
                },
                "5min": 0,
                "year": "2025",
                "month": "01",
                "day": "15",
                "hour": "08",
                "min": "00",
                "_source_job_timestamp": "2025-01-15T06:00:00Z"
            }
        ]

        # New record with newer source timestamp
        new_data = [
            {
                "eventTime": "2025-01-15T10:00:00.000000",
                "event_time": "2025-01-15T10:00:00.000000",
                "pk": "proj-X_user-X",
                "data": {
                    "projectguid": "proj-X",
                    "project_type": "PHOTOBOOK",
                    "project_subtype": "STANDARD",
                    "userid": "user-X",
                    "inserted": "2025-01-15T07:00:00.000000",
                    "updated": "2025-01-15T10:00:00.000000",
                    "product_index": 1,
                    "product_type": "BOOK",
                    "productguid": "product-X",
                    "productimageid": "img-NEW",
                    "msp": "MSP1",
                    "mspid": "mspid-X",
                    "mediaid": "same-media-id",
                    "locationspec": "loc-NEW"
                },
                "5min": 0,
                "year": "2025",
                "month": "01",
                "day": "15",
                "hour": "10",
                "min": "00"
            }
        ]

        previous_df = spark_session.createDataFrame(previous_data, schema)
        new_df = spark_session.createDataFrame(new_data, ImageLoader.get_output_schema())

        # Setup stubs
        fake_transform_reader = FakeTransformOutputReader(spark_session, test_df=new_df)
        fake_filtered_reader = FakeFilteredOutputReader(spark_session, test_df=previous_df)
        fake_loader = FakeFilterLoader(spark=spark_session)
        fake_manifest_service = FakeManifestService(
            previous_manifest=FilterManifest(run_id="prev", status="SUCCESS", output_path="s3://test/prev")
        )

        transformer = FilterTransformer(
            dedup_key_columns=["data.mediaid"],
            dedup_order_column="eventTime"
        )

        job = FilterImagesJob(
            transform_output_reader=fake_transform_reader,
            filtered_output_reader=fake_filtered_reader,
            transformer=transformer,
            loader=fake_loader,
            manifest_service=fake_manifest_service,
            base_path="s3://test/filtered_images",
            timezone_name="America/Los_Angeles",
            time_column="eventTime",
            event_publisher=NoopJobEventPublisher()
        )

        job.execute_job(
            transform_output_path="s3://test/transformed",
            triggered_by_job="transform_images",
            triggered_by_run_id="transform-test",
            year=2025,
            month=1,
            day=15
        )

        # Validate: should only have NEW record (last wins)
        actual_df = fake_loader.get_written_data()
        assert actual_df.count() == 1, "Should have exactly 1 record after dedup"

        # Verify it's the NEW version
        row = actual_df.collect()[0]
        assert row["data"]["productimageid"] == "img-NEW", \
            "Should keep NEW record (last duplicate wins)"
        assert row["data"]["locationspec"] == "loc-NEW", \
            "Should keep NEW record data"

        print("Test PASSED: Last-duplicate-wins always keeps newer record")

    def _get_schema_with_source_timestamp(self) -> StructType:
        """Get output schema with _source_job_timestamp column."""
        base_schema = ImageLoader.get_output_schema()
        return StructType(
            base_schema.fields + [StructField("_source_job_timestamp", StringType(), True)]
        )

    def _validate_output(self, actual_df: DataFrame, expected_df: DataFrame):
        """Validate the job output matches expectations."""
        # Compare by mediaid since that's the dedup key
        actual_mediaids = set(
            row["data"]["mediaid"] for row in actual_df.collect()
        )
        expected_mediaids = set(
            row["data"]["mediaid"] for row in expected_df.collect()
        )

        assert actual_mediaids == expected_mediaids, \
            f"MediaID mismatch.\nActual: {actual_mediaids}\nExpected: {expected_mediaids}"

        # Verify count
        assert actual_df.count() == expected_df.count(), \
            f"Count mismatch: actual={actual_df.count()}, expected={expected_df.count()}"

        # Verify specific updated records have new data
        actual_rows = {row["data"]["mediaid"]: row for row in actual_df.collect()}
        expected_rows = {row["data"]["mediaid"]: row for row in expected_df.collect()}

        for mediaid in expected_mediaids:
            actual_row = actual_rows[mediaid]
            expected_row = expected_rows[mediaid]

            # Check productimageid matches (this changes in updated records)
            assert actual_row["data"]["productimageid"] == expected_row["data"]["productimageid"], \
                f"productimageid mismatch for {mediaid}"


# =============================================================================
# Stub Implementations - Only stub I/O, preserve business logic
# =============================================================================

class FakeTransformOutputReader(TransformOutputReader):
    """
    Test stub for TransformOutputReader - returns pre-loaded test data.
    """

    def __init__(
        self,
        spark: SparkSession,
        test_df: Optional[DataFrame] = None,
        raise_on_read: bool = False
    ):
        super().__init__(spark)
        self._test_df = test_df
        self._raise_on_read = raise_on_read

    def read(self, path: str) -> DataFrame:
        """Override to return pre-loaded test data."""
        if self._raise_on_read or self._test_df is None:
            raise ValueError(f"No data found at transform output path: {path}")
        return self._test_df


class FakeFilteredOutputReader(FilteredOutputReader):
    """
    Test stub for FilteredOutputReader - returns pre-loaded test data.
    """

    def __init__(
        self,
        spark: SparkSession,
        test_df: Optional[DataFrame] = None
    ):
        super().__init__(spark)
        self._test_df = test_df

    def read(self, path: str) -> Optional[DataFrame]:
        """Override to return pre-loaded test data."""
        return self._test_df


class FakeFilterLoader(FilterLoader):
    """
    Test stub for FilterLoader - only overrides S3 I/O.

    All business logic (repartitioning, metrics) executes normally.
    """

    def __init__(self, spark: SparkSession):
        super().__init__(spark=spark, max_records_per_file=500000)
        self._written_data: Optional[DataFrame] = None
        self._latest_data: Optional[DataFrame] = None

    def load(
        self,
        df: DataFrame,
        output_path: str,
        metrics: FilterImagesJobMetrics
    ) -> List[str]:
        """Override to capture output instead of writing to S3."""
        record_count = df.count()

        # Capture the data
        self._written_data = df

        # Update metrics
        metrics.output_path = output_path
        metrics.output_files = ["test_output.parquet"]
        metrics.bytes_written = record_count * 500  # Estimate
        metrics.records_written = record_count

        return ["test_output.parquet"]

    def write_latest(
        self,
        df: DataFrame,
        latest_path: str,
        metrics: FilterImagesJobMetrics
    ) -> None:
        """Override to capture latest output."""
        self._latest_data = df
        metrics.latest_output_path = latest_path

    def delete_output(self, path: str) -> bool:
        """No-op for tests."""
        return True

    def get_written_data(self) -> Optional[DataFrame]:
        """Get the data that was 'written'."""
        return self._written_data


class FakeManifestService(ManifestService):
    """
    Test stub for ManifestService - stores manifests in memory.
    """

    def __init__(self, previous_manifest: Optional[FilterManifest] = None):
        self._previous_manifest = previous_manifest
        self._manifests: dict = {}
        self._run_id_counter = 0

    def read_manifest(self, manifest_path: str) -> Optional[FilterManifest]:
        return self._manifests.get(manifest_path)

    def write_manifest(self, manifest: FilterManifest, manifest_path: str) -> None:
        self._manifests[manifest_path] = manifest

    def list_manifests(self, manifests_dir: str) -> List[str]:
        return [p for p in self._manifests.keys() if p.startswith(manifests_dir)]

    def delete_path(self, path: str) -> None:
        keys_to_delete = [k for k in self._manifests.keys() if k.startswith(path)]
        for key in keys_to_delete:
            del self._manifests[key]

    def get_latest_manifest(
        self,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int
    ) -> Optional[FilterManifest]:
        """Return pre-configured previous manifest."""
        return self._previous_manifest

    def generate_run_id(self) -> str:
        self._run_id_counter += 1
        return f"filter-test-{self._run_id_counter:04d}"
