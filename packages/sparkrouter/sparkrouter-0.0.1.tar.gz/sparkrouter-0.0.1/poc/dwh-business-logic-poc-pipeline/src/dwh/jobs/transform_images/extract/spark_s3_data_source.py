from datetime import datetime, timedelta
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType


class SparkS3DataSource:
    """
    Data source for reading JSONL data from S3 using Spark.

    This class handles:
    - Partition path generation based on date range and configurable pattern
    - S3 I/O (isolated in _read_raw_json_from_s3 for testing)
    - Data validation, filtering, and metrics collection

    For testing, subclass and override ONLY _read_raw_json_from_s3() to inject test data.
    All business logic (partition generation, corrupt record handling, null filtering, metrics)
    will still execute.
    """

    def __init__(
        self,
        spark: SparkSession,
        base_path: str = None,
        partition_interval_minutes: int = 5
    ):
        """
        Initialize S3 data source with partition configuration.

        Args:
            spark: SparkSession
            base_path: Base S3 path (e.g., s3://bucket/data)
            partition_interval_minutes: Size of time partitions in minutes (default: 5)
        """
        self.spark = spark
        self.base_path = base_path.rstrip('/') if base_path else None
        self.partition_interval_minutes = partition_interval_minutes

    def _generate_partition_paths(self, start_date_utc: datetime, end_date_utc: datetime) -> list[str]:
        """
        Generate list of S3 partition paths based on UTC date range.

        Path pattern: {base_path}/year={year}/month={month}/day={day}/hour={HH}/min={MM}/*

        Args:
            start_date_utc: Start of date range (inclusive)
            end_date_utc: End of date range (exclusive)

        Returns:
            List of S3 paths covering the date range
        """
        if not self.base_path:
            raise ValueError("base_path must be configured to generate partition paths")

        paths = []
        interval = self.partition_interval_minutes
        current = start_date_utc.replace(
            minute=(start_date_utc.minute // interval) * interval,
            second=0,
            microsecond=0
        )

        while current < end_date_utc:
            path = (
                f"{self.base_path}"
                f"/year={current.year}"
                f"/month={current.month:02d}"
                f"/day={current.day:02d}"
                f"/hour={current.hour:02d}"
                f"/min={current.minute:02d}/*"
            )
            paths.append(path)
            current += timedelta(minutes=interval)

        return paths

    def _read_raw_json_from_s3(self, paths: list[str], schema: StructType) -> DataFrame:
        """
        Read raw JSONL files from S3 paths.

        This is the ONLY method that performs S3 I/O. Override this method in tests
        to inject test data while preserving all business logic.

        Args:
            paths: List of S3 paths (can include wildcards)
            schema: Schema for the JSON data

        Returns:
            Raw DataFrame from S3 (may contain corrupt records, nulls, etc.)

        Raises:
            Exception: If S3 read fails (e.g., path doesn't exist)
        """
        return (self.spark.read
                .schema(schema)
                .option("mode", "PERMISSIVE")
                .option("columnNameOfCorruptRecord", "_corrupt_record")
                .json(paths))

    def read_json(self, paths: list[str], schema: StructType, metrics=None) -> tuple[DataFrame, DataFrame]:
        """
        Read JSONL files from S3 paths, applying validation and collecting metrics.

        BUSINESS LOGIC (always executes, even in tests):
        1. Read raw data from S3 (via _read_raw_json_from_s3)
        2. Handle corrupt records (malformed JSON)
        3. Filter null eventTime and data fields
        4. Collect metrics in single aggregation pass
        5. Separate valid and dropped records

        Args:
            paths: List of S3 paths to read
            schema: Schema for the JSON data
            metrics: Optional metrics object to populate

        Returns:
            Tuple of (valid_df, dropped_df)
            - valid_df: Records with valid eventTime and data fields
            - dropped_df: Records that were dropped (corrupt, missing fields)
        """
        from pyspark.sql.functions import (
            count, sum as spark_sum, when, col, lit, min as spark_min, max as spark_max
        )

        # Handle empty paths
        if not paths:
            from pyspark.sql.functions import lit as spark_lit
            empty_df = self.spark.createDataFrame([], schema)
            empty_dropped_df = empty_df.withColumn("drop_reason", spark_lit(None).cast("string")) \
                                        .withColumn("drop_phase", spark_lit(None).cast("string"))
            return empty_df, empty_dropped_df

        if metrics:
            metrics.extract_partitions_requested = len(paths)

        # Read raw data from S3 (this is the only S3 I/O operation)
        print(f"[EXTRACT] Reading {len(paths)} partition paths")
        try:
            df_all = self._read_raw_json_from_s3(paths, schema)
        except Exception as e:
            print(f"[EXTRACT] Error reading paths: {e}")
            if metrics:
                metrics.extract_partitions_found = 0
                metrics.extract_records_read = 0
                metrics.extract_records_after_filter = 0
            from pyspark.sql.functions import lit as spark_lit
            empty_df = self.spark.createDataFrame([], schema)
            empty_dropped_df = empty_df.withColumn("drop_reason", spark_lit(None).cast("string")) \
                                        .withColumn("drop_phase", spark_lit(None).cast("string"))
            return empty_df, empty_dropped_df

        # BUSINESS LOGIC: Cache df_all since it's used for:
        # 1. Metrics aggregation
        # 2. Valid records filter
        # 3. Dropped records filter
        df_all.cache()
        print("[EXTRACT] Cached unified DataFrame for metrics + filtering")

        # BUSINESS LOGIC: Single-pass metrics collection using SQL aggregation
        # Check if _corrupt_record column exists (only present if PERMISSIVE mode found corrupt records)
        has_corrupt_column = "_corrupt_record" in df_all.columns

        if has_corrupt_column:
            # Build aggregation with corrupt record tracking
            metrics_row = df_all.agg(
                count("*").alias("total_records"),
                spark_sum(when(col("_corrupt_record").isNotNull(), 1).otherwise(0)).alias("corrupt_records"),
                spark_sum(when(col("eventTime").isNull(), 1).otherwise(0)).alias("null_eventtime"),
                spark_sum(when(col("data").isNull(), 1).otherwise(0)).alias("null_data"),
                spark_sum(when(
                    (col("_corrupt_record").isNull()) &
                    (col("eventTime").isNotNull()) &
                    (col("data").isNotNull()), 1
                ).otherwise(0)).alias("valid_records"),
                spark_min(col("eventTime")).alias("min_event_time"),
                spark_max(col("eventTime")).alias("max_event_time")
            ).collect()[0]
        else:
            # No corrupt records detected - simplified aggregation
            metrics_row = df_all.agg(
                count("*").alias("total_records"),
                lit(0).alias("corrupt_records"),
                spark_sum(when(col("eventTime").isNull(), 1).otherwise(0)).alias("null_eventtime"),
                spark_sum(when(col("data").isNull(), 1).otherwise(0)).alias("null_data"),
                spark_sum(when(
                    (col("eventTime").isNotNull()) &
                    (col("data").isNotNull()), 1
                ).otherwise(0)).alias("valid_records"),
                spark_min(col("eventTime")).alias("min_event_time"),
                spark_max(col("eventTime")).alias("max_event_time")
            ).collect()[0]

        # Extract metrics from aggregation result (use 0 for None values from spark_sum)
        total_records = metrics_row['total_records'] or 0
        corrupt_records = metrics_row['corrupt_records'] or 0
        null_eventtime = metrics_row['null_eventtime'] or 0
        null_data = metrics_row['null_data'] or 0
        valid_records = metrics_row['valid_records'] or 0
        min_event_time = metrics_row['min_event_time']
        max_event_time = metrics_row['max_event_time']

        # Handle empty result
        if total_records == 0:
            print("[EXTRACT] No records found in any partition")
            df_all.unpersist()
            if metrics:
                metrics.extract_partitions_found = 0
                metrics.extract_records_read = 0
                metrics.extract_records_after_filter = 0
            from pyspark.sql.functions import lit as spark_lit
            empty_df = self.spark.createDataFrame([], schema)
            empty_dropped_df = empty_df.withColumn("drop_reason", spark_lit(None).cast("string")) \
                                        .withColumn("drop_phase", spark_lit(None).cast("string"))
            return empty_df, empty_dropped_df

        # Update metrics
        if metrics:
            metrics.extract_partitions_found = len(paths)  # Spark read all paths
            metrics.extract_records_read = total_records
            metrics.extract_corrupt_records = corrupt_records
            metrics.extract_null_eventtime = null_eventtime
            metrics.extract_null_data = null_data
            metrics.extract_records_after_filter = valid_records
            metrics.extract_min_event_time = min_event_time
            metrics.extract_max_event_time = max_event_time
            # Set common base class field for cross-job comparison
            metrics.records_read = total_records

            if corrupt_records > 0:
                metrics.record_drop("extract_corrupt_json", corrupt_records)
            if null_eventtime > 0:
                metrics.record_drop("extract_null_eventtime", null_eventtime)
            if null_data > 0:
                metrics.record_drop("extract_null_data", null_data)

        # Print summary
        if corrupt_records > 0:
            print(f"WARNING: Found {corrupt_records} corrupt/malformed records out of {total_records}")
        if null_eventtime > 0:
            print(f"WARNING: Found {null_eventtime} records with null 'eventTime' field")
        if null_data > 0:
            print(f"WARNING: Found {null_data} records with null 'data' field")
        print(f"[EXTRACT] Read {total_records} total records, {valid_records} valid after filtering")

        # Calculate event time range if available
        if min_event_time and max_event_time:
            try:
                from datetime import datetime
                min_dt = datetime.fromisoformat(min_event_time.replace('Z', '+00:00'))
                max_dt = datetime.fromisoformat(max_event_time.replace('Z', '+00:00'))
                event_time_range_hours = (max_dt - min_dt).total_seconds() / 3600
                print(f"[EXTRACT] Event time range: {min_event_time} to {max_event_time} ({event_time_range_hours:.2f} hours)")
                if metrics:
                    metrics.extract_event_time_range_hours = event_time_range_hours
            except Exception as e:
                print(f"WARNING: Could not parse event time range: {e}")

        # BUSINESS LOGIC: Separate valid and dropped records (uses cached df_all - no re-scan)
        from pyspark.sql.functions import lit as spark_lit

        if has_corrupt_column:
            valid_df = df_all.filter(
                (col("_corrupt_record").isNull()) &
                (col("eventTime").isNotNull()) &
                (col("data").isNotNull())
            ).drop("_corrupt_record")

            dropped_df = df_all.filter(
                (col("_corrupt_record").isNotNull()) |
                (col("eventTime").isNull()) |
                (col("data").isNull())
            ).withColumn(
                "drop_reason",
                when(col("_corrupt_record").isNotNull(), spark_lit("extract_corrupt_json"))
                .when(col("eventTime").isNull(), spark_lit("extract_null_eventtime"))
                .when(col("data").isNull(), spark_lit("extract_null_data"))
                .otherwise(spark_lit("extract_unknown"))
            ).withColumn("drop_phase", spark_lit("extract"))
        else:
            valid_df = df_all.filter(
                (col("eventTime").isNotNull()) &
                (col("data").isNotNull())
            )

            dropped_df = df_all.filter(
                (col("eventTime").isNull()) |
                (col("data").isNull())
            ).withColumn(
                "drop_reason",
                when(col("eventTime").isNull(), spark_lit("extract_null_eventtime"))
                .when(col("data").isNull(), spark_lit("extract_null_data"))
                .otherwise(spark_lit("extract_unknown"))
            ).withColumn("drop_phase", spark_lit("extract"))

        # Note: df_all cache will be released when valid_df/dropped_df are no longer needed
        # The filters are lazy, so cache is used when downstream actions execute

        return valid_df, dropped_df

    def read_json_for_date_range(
        self,
        start_date_utc: datetime,
        end_date_utc: datetime,
        schema: StructType,
        metrics=None
    ) -> tuple[DataFrame, DataFrame]:
        """
        Read JSONL files for a date range, generating partition paths automatically.

        This is the primary method for extractors to use. It combines:
        1. Partition path generation based on date range
        2. S3 reading with validation and metrics

        Args:
            start_date_utc: Start of date range (inclusive)
            end_date_utc: End of date range (exclusive)
            schema: Schema for the JSON data
            metrics: Optional metrics object to populate

        Returns:
            Tuple of (valid_df, dropped_df)
        """
        start_date_str = start_date_utc.strftime('%Y-%m-%d %H:%M:%S')
        end_date_str = end_date_utc.strftime('%Y-%m-%d %H:%M:%S')

        partition_paths = self._generate_partition_paths(start_date_utc, end_date_utc)
        print(f"[EXTRACT] Date range: {start_date_str} to {end_date_str}")
        print(f"[EXTRACT] Generated {len(partition_paths)} partition paths")
        print(f"[EXTRACT] Partition paths: {partition_paths}")

        return self.read_json(partition_paths, schema, metrics)
