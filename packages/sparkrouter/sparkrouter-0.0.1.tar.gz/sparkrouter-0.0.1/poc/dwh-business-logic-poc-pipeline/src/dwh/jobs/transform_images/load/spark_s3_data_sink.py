from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.functions import (
    col,
    struct,
    minute,
    hour,
    dayofmonth,
    month,
    year,
    to_timestamp,
    to_json,
    lpad
)


class SparkS3DataSink:
    """
    Data sink for writing JSONL data to S3 using Spark.

    This class handles:
    - Time-based partition column generation
    - S3 I/O (isolated in _*_s3_*() methods for testing)
    - JSON conversion and file size control

    For testing, subclass and override ONLY the _*_s3_*() methods to stub S3 I/O.
    All business logic (partition generation, JSON conversion) will still execute.
    """

    def __init__(
        self,
        spark: SparkSession,
        base_path: str = None,
        partition_interval_minutes: int = 5,
        max_records_per_file: int = None
    ):
        """
        Initialize S3 data sink with partition and file size configuration.

        Args:
            spark: SparkSession for accessing Hadoop FileSystem
            base_path: Base S3 path (e.g., s3://bucket/output)
            partition_interval_minutes: Size of time partitions in minutes (default: 5)
            max_records_per_file: Maximum number of records per output file.
                                 Default is None (uses Spark defaults).
                                 For 256MB files with ~1KB records, use ~262000.
        """
        self.spark = spark
        self.base_path = base_path.rstrip('/') if base_path else None
        self.partition_interval_minutes = partition_interval_minutes
        self.max_records_per_file = max_records_per_file

    def add_partition_columns(self, df: DataFrame, timestamp_column: str) -> DataFrame:
        """
        Add time-based partition columns to a DataFrame.

        Adds: year, month, day, hour, min (and {interval}min as integer)

        Args:
            df: Input DataFrame
            timestamp_column: Name of column containing timestamp string (ISO format)

        Returns:
            DataFrame with partition columns added
        """
        interval = self.partition_interval_minutes

        return df.withColumn(
            "_event_timestamp",
            to_timestamp(col(timestamp_column), "yyyy-MM-dd'T'HH:mm:ss'Z'")
        ).withColumn(
            "year", year(col("_event_timestamp")).cast("string")
        ).withColumn(
            "month", lpad(month(col("_event_timestamp")).cast("string"), 2, "0")
        ).withColumn(
            "day", lpad(dayofmonth(col("_event_timestamp")).cast("string"), 2, "0")
        ).withColumn(
            "hour", lpad(hour(col("_event_timestamp")).cast("string"), 2, "0")
        ).withColumn(
            "min", lpad(((minute(col("_event_timestamp")) / interval).cast("int") * interval).cast("string"), 2, "0")
        ).withColumn(
            f"{interval}min", (minute(col("_event_timestamp")) / interval).cast("int") * interval
        ).drop("_event_timestamp")

    def get_partition_columns(self) -> list[str]:
        """
        Get the list of partition column names.

        Returns:
            List of partition column names: ["year", "month", "day", "hour", "min"]
        """
        return ["year", "month", "day", "hour", "min"]

    def _write_text_to_s3(self, df: DataFrame, path: str, partition_by: list[str]) -> None:
        """
        Write DataFrame as text to S3 with partitioning.

        This is the ONLY method that performs S3 write I/O. Override this method
        in tests to capture output while preserving all business logic.

        Args:
            df: DataFrame with 'value' column and partition columns
            path: S3 output path
            partition_by: Columns to partition by
        """
        df.write.mode("overwrite").partitionBy(*partition_by).option(
            "maxRecordsPerFile", self.max_records_per_file or 0
        ).text(path)

    def _delete_s3_objects(self, bucket: str, prefix: str) -> int:
        """
        Delete all objects under an S3 prefix.

        This is the ONLY method that performs S3 delete I/O. Override this method
        in tests to skip actual deletion while preserving partition path building logic.

        Args:
            bucket: S3 bucket name
            prefix: S3 key prefix (partition path)

        Returns:
            Number of objects deleted
        """
        import boto3

        s3_client = boto3.client('s3')
        deleted_count = 0

        paginator = s3_client.get_paginator('list_objects_v2')
        pages = paginator.paginate(Bucket=bucket, Prefix=f"{prefix}/")

        for page in pages:
            if 'Contents' not in page:
                continue

            objects_to_delete = [{'Key': obj['Key']} for obj in page['Contents']]

            if objects_to_delete:
                response = s3_client.delete_objects(
                    Bucket=bucket,
                    Delete={'Objects': objects_to_delete}
                )
                deleted_count += len(response.get('Deleted', []))

        return deleted_count

    def _list_s3_files(self, path: str) -> tuple[list[str], int]:
        """
        Recursively list all .txt files at an S3 path.

        This is the ONLY method that performs S3 list I/O. Override this method
        in tests to return mock file lists while preserving all business logic.

        Args:
            path: S3 path to list

        Returns:
            Tuple of (file_paths, total_bytes)
        """
        try:
            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            fs = self.spark._jvm.org.apache.hadoop.fs.FileSystem.get(
                self.spark._jvm.java.net.URI(path),
                hadoop_conf
            )

            path_obj = self.spark._jvm.org.apache.hadoop.fs.Path(path)

            file_paths = []
            total_bytes = 0
            file_iterator = fs.listFiles(path_obj, True)  # True = recursive

            while file_iterator.hasNext():
                file_status = file_iterator.next()
                file_path = str(file_status.getPath())

                # Only include .txt files (exclude _SUCCESS, .crc, etc.)
                if file_path.endswith('.txt'):
                    file_paths.append(file_path)
                    total_bytes += file_status.getLen()

            return sorted(file_paths), total_bytes
        except Exception as e:
            print(f"WARNING: Could not list output files: {e}")
            return [], 0

    def write_json(self, df: DataFrame, path: str, partition_by: list[str], row_count_hint: int = None) -> tuple[list[str], int]:
        """
        Write DataFrame as JSON lines to S3 with partitioning.

        BUSINESS LOGIC (always executes, even in tests):
        1. Convert non-partition columns to JSON string
        2. Repartition based on record count for file size control
        3. Write to S3 (via _write_text_to_s3)
        4. List written files (via _list_s3_files)

        Args:
            df: DataFrame to write
            path: S3 output path
            partition_by: Columns to partition by
            row_count_hint: Optional pre-computed row count to avoid count() action

        Returns:
            Tuple of (file_paths, total_bytes)
        """
        # BUSINESS LOGIC: Convert non-partition columns to JSON string
        non_partition_cols = [c for c in df.columns if c not in partition_by]

        json_str_df = df.select(
            to_json(struct(*[col(c) for c in non_partition_cols])).alias("value"),
            *[col(c) for c in partition_by]
        )

        # BUSINESS LOGIC: Repartition to control file sizes if configured
        if self.max_records_per_file:
            row_count = row_count_hint if row_count_hint is not None else json_str_df.count()
            num_partitions = max(1, (row_count + self.max_records_per_file - 1) // self.max_records_per_file)
            json_str_df = json_str_df.repartition(num_partitions, *partition_by)

        # S3 I/O: Write to S3
        self._write_text_to_s3(json_str_df, path, partition_by)

        # S3 I/O: List files written
        return self._list_s3_files(path)

    def clean_partitions(self, base_path: str, partition_summary, partition_columns: list[str]) -> int:
        """
        Delete existing data in target partitions before writing.

        BUSINESS LOGIC (always executes, even in tests):
        1. Parse S3 path to extract bucket and prefix
        2. Build partition paths from summary rows
        3. Delete objects (via _delete_s3_objects)

        Args:
            base_path: Base S3 path (e.g., s3://bucket/transformed_images)
            partition_summary: List of Row objects containing partition values
            partition_columns: List of partition column names

        Returns:
            Number of objects deleted
        """
        from urllib.parse import urlparse

        # BUSINESS LOGIC: Parse S3 path
        parsed = urlparse(base_path)
        bucket = parsed.netloc
        prefix = parsed.path.lstrip('/')

        print(f"[S3DataSink] Cleaning sink partitions in s3://{bucket}/{prefix}")

        deleted_count = 0

        # BUSINESS LOGIC: Build partition paths and delete
        for row in partition_summary:
            partition_path = prefix
            for col_name in partition_columns:
                value = getattr(row, col_name)
                partition_path = f"{partition_path}/{col_name}={value}"

            print(f"[S3DataSink]   Deleting partition: s3://{bucket}/{partition_path}/")

            # S3 I/O: Delete objects in this partition
            deleted_count += self._delete_s3_objects(bucket, partition_path)

        if deleted_count > 0:
            print(f"[S3DataSink] Deleted {deleted_count} existing objects from sink partitions")
        else:
            print(f"[S3DataSink] No existing objects found in sink partitions")

        return deleted_count
