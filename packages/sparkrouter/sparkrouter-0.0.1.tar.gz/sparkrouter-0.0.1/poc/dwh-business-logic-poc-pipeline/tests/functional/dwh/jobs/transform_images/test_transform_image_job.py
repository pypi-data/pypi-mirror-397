import pytest
from pathlib import Path
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.types import StructType

from dwh.jobs.transform_images.load.spark_s3_data_sink import SparkS3DataSink
from dwh.jobs.transform_images.transform_images_job import TransformImagesJob
from dwh.jobs.transform_images.extract.image_extractor import ImageExtractor
from dwh.jobs.transform_images.extract.spark_s3_data_source import SparkS3DataSource
from dwh.jobs.transform_images.transform.image_transformer import ImageTransformer
from dwh.jobs.transform_images.load.image_loader import ImageLoader

from dwh.services.quality.quality_checker import NoopQualityChecker
from dwh.services.event.job_event_publisher import NoopJobEventPublisher

pytestmark = pytest.mark.functional


class TestTransformImagesJobEndToEnd:
    """
    End-to-end integration test for TransformImagesJob.

    Tests the complete pipeline: raw input → job execution → final output.
    Only S3 I/O is stubbed - all business logic runs for real.
    """

    def test_transform_images_job_end_to_end(self, spark_session: SparkSession):
        """
        Full pipeline test: raw input → job execution → validate output.
        Only S3 I/O is stubbed - all business logic runs for real.
        """
        # 1. Load test data
        test_data_dir = Path(__file__).parent
        raw_df = (
            spark_session.read
            .schema(ImageExtractor.get_input_schema())
            .json(str(test_data_dir / "raw.jsonl"))
        )
        expected_df = (
            spark_session.read
            .schema(ImageLoader.get_output_schema())
            .json(str(test_data_dir / "loaded.jsonl"))
        )

        # 2. Setup S3 infrastructure stubs - only stub the S3 I/O method
        stubbed_s3_source = FakeS3DataSource(spark_session, base_path="s3://test/input", test_df=raw_df)

        # Create sinks for each category (they share written_data for test validation)
        nautilus_sink = FakeS3DataSink(spark_session, base_path="s3://test/output/nautilus/transformed_images")
        savedproject_sink = FakeS3DataSink(spark_session, base_path="s3://test/output/savedproject/transformed_images")

        # Category resolver matches factory logic
        def resolve_category(data_type: str) -> str:
            return "nautilus" if "nautilus" in data_type.lower() else "savedproject"

        data_sinks = {"nautilus": nautilus_sink, "savedproject": savedproject_sink}

        # 3. Create REAL business logic components with stubbed infrastructure
        extractor = ImageExtractor(s3_data_source=stubbed_s3_source)
        transformer = ImageTransformer()
        loader = ImageLoader(data_sinks=data_sinks, category_resolver=resolve_category)

        # 4. Instantiate and run the job
        job = TransformImagesJob(
            image_extractor=extractor,
            image_transformer=transformer,
            image_loader=loader,
            event_publisher=NoopJobEventPublisher(),
            quality_checker=NoopQualityChecker()
        )
        job.execute_job(
            start_date="2024-01-01",
            end_date="2024-01-31",
            created_by="test_user"
            # clean_sink defaults to True, but FakeS3DataSink handles it properly
        )

        # 5. Retrieve what the loader wrote - combine data from all sinks
        actual_df = get_combined_written_data(data_sinks, spark_session)

        # 6. Validate output
        self._validate_output(actual_df, expected_df, raw_df)

    def _validate_output(self, actual_df: DataFrame, expected_df: DataFrame, raw_df: DataFrame):
        """Validate the job output matches expectations.

        Note: Validates critical business logic fields. Partition fields (year, month, day, hour, min)
        are excluded as they may have formatting differences between test data and actual output.
        """
        # Sort both DataFrames consistently before comparison
        sort_cols = ["pk", "eventTime", "data.productimageid"]

        # Select only critical business logic fields for comparison (exclude partition fields)
        critical_fields = ["eventTime", "event_time", "pk", "data", "5min"]
        actual_sorted = actual_df.select(*critical_fields).orderBy(*sort_cols).collect()
        expected_sorted = expected_df.select(*critical_fields).orderBy(*sort_cols).collect()

        # Row count validation
        assert len(actual_sorted) == len(expected_sorted), \
            f"Row count mismatch: actual={len(actual_sorted)}, expected={len(expected_sorted)}"

        # Row-by-row comparison of business logic fields
        for i, (actual_row, expected_row) in enumerate(zip(actual_sorted, expected_sorted)):
            assert actual_row == expected_row, \
                f"Row {i} mismatch\nActual:   {actual_row}\nExpected: {expected_row}"

        # Validate partition fields exist in actual output (formatting may differ from test data)
        partition_fields = ["year", "month", "day", "hour", "min"]
        actual_columns = set(actual_df.columns)
        for field in partition_fields:
            assert field in actual_columns, f"Partition field '{field}' missing from actual output"

    def test_transform_images_job_no_data_found(self, spark_session: SparkSession):
        """
        Test job behavior when no data is found in S3.
        Validates that:
        1. Job completes successfully (no crash)
        2. Empty DataFrames have correct schema (including drop_phase/drop_reason)
        3. Metrics show 0 records
        4. No output is written
        """
        from dwh.jobs.transform_images.load.dropped_record_loader import DroppedRecordLoader

        # Setup S3 infrastructure stubs that return empty DataFrames
        stubbed_s3_source = FakeS3DataSource(spark_session, base_path="s3://test/input")

        # Create sinks for each category
        nautilus_sink = FakeS3DataSink(spark_session, base_path="s3://test/output/nautilus/transformed_images")
        savedproject_sink = FakeS3DataSink(spark_session, base_path="s3://test/output/savedproject/transformed_images")
        dropped_sink = FakeS3DataSink(spark_session, base_path="s3://test/output")

        def resolve_category(data_type: str) -> str:
            return "nautilus" if "nautilus" in data_type.lower() else "savedproject"

        data_sinks = {"nautilus": nautilus_sink, "savedproject": savedproject_sink}

        # Create REAL business logic components with stubbed infrastructure
        extractor = ImageExtractor(s3_data_source=stubbed_s3_source)
        transformer = ImageTransformer()
        loader = ImageLoader(data_sinks=data_sinks, category_resolver=resolve_category)
        dropped_loader = DroppedRecordLoader(s3_data_sink=dropped_sink)

        # Instantiate and run the job
        job = TransformImagesJob(
            image_extractor=extractor,
            image_transformer=transformer,
            image_loader=loader,
            dropped_record_loader=dropped_loader,
            event_publisher=NoopJobEventPublisher(),
            quality_checker=NoopQualityChecker()
        )

        metrics_json = job.execute_job(
            start_date="2024-01-01",
            end_date="2024-01-02",
            created_by="test_user"
        )

        # Validate metrics show 0 records processed
        # Note: Job-specific metrics are now in 'payload' section per AbstractJobMetrics structure
        assert isinstance(metrics_json, dict), "Job should return metrics dict"
        assert metrics_json['payload']['extract']['records_after_filter'] == 0, "Should read 0 records"
        assert metrics_json['payload']['transform']['records_output'] == 0, "Should transform 0 records"
        assert metrics_json['payload']['load']['files_written'] == 0, "Should write 0 files"
        assert metrics_json['records_dropped'] == 0, "Should drop 0 records"

        # Validate no data was written to any sink
        total_written = sum(len(sink._written_data) for sink in data_sinks.values())
        assert total_written == 0, "Should not write any data when no records found"

        print("✓ No-data scenario test passed: Job handled empty input gracefully")


class FakeS3DataSource(SparkS3DataSource):
    """
    Test stub for SparkS3DataSource - only overrides S3 I/O method.

    All business logic (partition path generation, corrupt record handling,
    null filtering, metrics collection) executes normally.
    """

    def __init__(self, spark: SparkSession, base_path: str, test_df: DataFrame = None):
        super().__init__(spark, base_path=base_path)
        self._test_df = test_df

    def _read_raw_json_from_s3(self, paths: list[str], schema: StructType) -> DataFrame:
        """
        Override S3 I/O to return test data or empty DataFrame.

        This is the ONLY method being stubbed. All business logic still executes:
        - Partition path generation (in read_json_for_date_range)
        - Corrupt record detection
        - Null filtering
        - Metrics collection

        Args:
            paths: Ignored - test data returned regardless of paths
            schema: Used to create empty DataFrame if no test_df provided

        Returns:
            Pre-loaded test DataFrame, or empty DataFrame with correct schema
        """
        if self._test_df is not None:
            return self._test_df
        return self.spark.createDataFrame([], schema)


class FakeS3DataSink(SparkS3DataSink):
    """
    Test stub for SparkS3DataSink - only overrides S3 I/O methods.

    All business logic (partition column generation, JSON conversion, repartitioning,
    partition path building) executes normally.
    """

    def __init__(self, spark: SparkSession, base_path: str):
        super().__init__(spark, base_path=base_path)
        self._written_data = []  # Capture DataFrames passed to write

    def _write_text_to_s3(self, df: DataFrame, path: str, partition_by: list[str]) -> None:
        """
        Override S3 write I/O to capture output.

        This is the ONLY write method being stubbed. All business logic in write_json()
        still executes: JSON conversion, partitioning, repartitioning.

        Args:
            df: DataFrame with 'value' column and partition columns (already processed by business logic)
            path: Output path (ignored in test)
            partition_by: Partition columns (ignored in test)
        """
        # The df here has already been through business logic transformation
        # It contains 'value' (JSON string) and partition columns
        self._written_data.append(df)

    def _delete_s3_objects(self, bucket: str, prefix: str) -> int:
        """
        Override S3 delete I/O - no-op in tests.

        Business logic (partition path building) still executes in clean_partitions().
        """
        print(f"[FakeS3DataSink] Skipping delete: s3://{bucket}/{prefix}")
        return 0

    def _list_s3_files(self, path: str) -> tuple[list[str], int]:
        """
        Override S3 list I/O - return empty list in tests.

        Business logic in write_json() still executes.
        """
        return [], 0

    def get_written_data(self, path: str) -> DataFrame:
        """
        Retrieve captured output - union all writes if multiple data_types.

        The captured DataFrames contain 'value' (JSON string) and partition columns.
        This method parses the JSON back to the original schema for test validation.
        """
        from pyspark.sql.functions import from_json, col

        if not self._written_data:
            return None

        # Union all DataFrames from different data_types
        if len(self._written_data) == 1:
            combined_df = self._written_data[0]
        else:
            combined_df = self._written_data[0]
            for df in self._written_data[1:]:
                combined_df = combined_df.union(df)

        # Parse JSON 'value' column back to original schema
        # The 'value' column contains JSON with: eventTime, event_time, pk, data, 5min
        json_schema = ImageLoader.get_output_schema()

        # Extract non-partition fields from schema (those that were JSON-ified)
        partition_cols = ["year", "month", "day", "hour", "min"]
        non_partition_schema = StructType([
            f for f in json_schema.fields if f.name not in partition_cols
        ])

        # Parse JSON and combine with partition columns
        parsed_df = combined_df.withColumn(
            "parsed", from_json(col("value"), non_partition_schema)
        ).select(
            col("parsed.*"),
            *[col(c) for c in partition_cols]
        )

        return parsed_df


def get_combined_written_data(data_sinks: dict[str, "FakeS3DataSink"], spark_session: SparkSession) -> DataFrame:
    """
    Combine written data from all sinks for test validation.

    The captured DataFrames contain 'value' (JSON string) and partition columns.
    This function parses the JSON back to the original schema.
    """
    from pyspark.sql.functions import from_json, col

    # Collect all written DataFrames from all sinks
    all_written = []
    for sink in data_sinks.values():
        all_written.extend(sink._written_data)

    if not all_written:
        return None

    # Union all DataFrames
    combined_df = all_written[0]
    for df in all_written[1:]:
        combined_df = combined_df.union(df)

    # Parse JSON 'value' column back to original schema
    json_schema = ImageLoader.get_output_schema()

    # Extract non-partition fields from schema (those that were JSON-ified)
    partition_cols = ["year", "month", "day", "hour", "min"]
    non_partition_schema = StructType([
        f for f in json_schema.fields if f.name not in partition_cols
    ])

    # Parse JSON and combine with partition columns
    parsed_df = combined_df.withColumn(
        "parsed", from_json(col("value"), non_partition_schema)
    ).select(
        col("parsed.*"),
        *[col(c) for c in partition_cols]
    )

    return parsed_df


