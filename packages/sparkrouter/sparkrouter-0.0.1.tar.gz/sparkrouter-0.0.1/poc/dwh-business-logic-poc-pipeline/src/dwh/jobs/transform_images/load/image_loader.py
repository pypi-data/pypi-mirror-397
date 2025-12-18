from dataclasses import dataclass, field
from typing import Callable

from pyspark.sql import DataFrame
from pyspark.sql.functions import concat_ws, col, struct, count as spark_count
from pyspark.sql.types import StructType, StringType, StructField, IntegerType

from dwh.jobs.transform_images.load.spark_s3_data_sink import SparkS3DataSink


@dataclass
class LoadResults:
    """Accumulator for load operation results."""
    total_records: int = 0
    total_files: int = 0
    total_partitions: int = 0
    total_bytes: int = 0
    total_deleted: int = 0
    bytes_by_category: dict = field(default_factory=dict)
    files_by_category: dict = field(default_factory=dict)
    output_paths: list = field(default_factory=list)
    output_paths_by_category: dict = field(default_factory=dict)

    def add_category_result(
        self,
        category: str,
        records: int,
        files: int,
        partitions: int,
        bytes_written: int,
        deleted: int,
        paths: list[str]
    ):
        self.total_records += records
        self.total_files += files
        self.total_partitions += partitions
        self.total_bytes += bytes_written
        self.total_deleted += deleted
        self.bytes_by_category[category] = self.bytes_by_category.get(category, 0) + bytes_written
        self.files_by_category[category] = self.files_by_category.get(category, 0) + files
        self.output_paths.extend(paths)
        if category not in self.output_paths_by_category:
            self.output_paths_by_category[category] = []
        self.output_paths_by_category[category].extend(paths)


class ImageLoader:
    """
    Loads transformed image data to configured sinks.

    This class handles image-specific concerns:
    - Output data structure (pk, data struct, eventTime)
    - Routing data to appropriate sinks based on data_type

    Storage concerns (partitioning, paths, S3/database) are fully abstracted
    via the data_sinks map provided at construction.
    """

    def __init__(
        self,
        data_sinks: dict[str, SparkS3DataSink],
        category_resolver: Callable[[str], str]
    ):
        """
        Initialize ImageLoader with category-to-sink mapping.

        Args:
            data_sinks: Map of category name to sink (e.g., {"nautilus": sink1, "savedproject": sink2})
            category_resolver: Function that maps data_type value to category name
        """
        self.data_sinks = data_sinks
        self.category_resolver = category_resolver
        self._reference_sink = next(iter(data_sinks.values()))

    def load(self, df: DataFrame, metrics=None, clean_sink: bool = True) -> None:
        """Write transformed DataFrame to configured sinks.

        Args:
            df: DataFrame to write (must include data_type column)
            metrics: Optional metrics collector
            clean_sink: If True, delete existing data in target partitions before writing
        """
        # Get input count
        input_count = self._get_input_count(df, metrics)
        print(f"[LOAD] clean_sink={clean_sink}")

        if input_count == 0:
            print("[LOAD] No data to load. Skipping write operation.")
            return

        # Prepare output DataFrame
        partition_columns = self._reference_sink.get_partition_columns()
        out_df = self._prepare_output_dataframe(df, partition_columns)

        # Cache if large dataset
        if input_count >= 10000:
            out_df.cache()
            print("[LOAD] Output DataFrame cached (large dataset)")

        # Aggregate partition info across all data types
        partition_data, data_type_counts = self._aggregate_partitions(out_df, partition_columns)

        print(f"[LOAD] Data types to process: {list(partition_data.keys())}")
        print(f"[LOAD] Partition columns: {partition_columns}")

        # Process each data type
        results = LoadResults()
        for data_type in partition_data.keys():
            self._process_data_type(
                out_df, data_type, partition_data[data_type], data_type_counts[data_type],
                partition_columns, clean_sink, results
            )

        # Validate and summarize
        self._print_summary(results, input_count, clean_sink)

        # Update metrics
        self._update_metrics(metrics, results, input_count, clean_sink)

    def _get_input_count(self, df: DataFrame, metrics) -> int:
        """Get input record count, preferring cached transform metrics."""
        if metrics and hasattr(metrics, 'transform_records_output') and metrics.transform_records_output is not None:
            count = metrics.transform_records_output
            print(f"[LOAD] Starting load with {count} input records (from transform metrics)")
        else:
            count = df.count()
            print(f"[LOAD] Starting load with {count} input records (counted)")

        if metrics:
            metrics.load_records_input = count

        return count

    def _prepare_output_dataframe(self, df: DataFrame, partition_columns: list[str]) -> DataFrame:
        """Transform input DataFrame to output structure with partitions."""
        interval = self._reference_sink.partition_interval_minutes
        df_with_partitions = self._reference_sink.add_partition_columns(df, "updated")

        df_with_pk = df_with_partitions.withColumn(
            "pk",
            concat_ws("_", col("projectguid"), col("userid"))
        )

        out_data = struct(
            col("projectguid"),
            col("project_type"),
            col("project_subtype"),
            col("userid"),
            col("inserted"),
            col("updated"),
            col("product_index"),
            col("product_type"),
            col("productguid"),
            col("productimageid"),
            col("msp"),
            col("mspid"),
            col("mediaid"),
            col("locationspec")
        )

        return df_with_pk.select(
            col("updated").alias("eventTime"),
            col("updated").alias("event_time"),
            col("pk"),
            out_data.alias("data"),
            col(f"{interval}min"),
            *[col(c) for c in partition_columns],
            col("data_type")
        )

    def _aggregate_partitions(
        self, out_df: DataFrame, partition_columns: list[str]
    ) -> tuple[dict, dict]:
        """Single aggregation for all data types and partitions."""
        all_partitions = out_df.groupBy("data_type", *partition_columns).agg(
            spark_count("*").alias("count")
        ).collect()

        partition_data = {}
        data_type_counts = {}

        for row in all_partitions:
            dt = row['data_type']
            if dt not in partition_data:
                partition_data[dt] = []
                data_type_counts[dt] = 0
            partition_data[dt].append(row)
            data_type_counts[dt] += row['count']

        return partition_data, data_type_counts

    def _process_data_type(
        self,
        out_df: DataFrame,
        data_type: str,
        partition_summary: list,
        record_count: int,
        partition_columns: list[str],
        clean_sink: bool,
        results: LoadResults
    ) -> None:
        """Process a single data type: clean partitions and write data."""
        print(f"\n[LOAD] Processing data_type: {data_type}")

        # Resolve category and sink
        category = self.category_resolver(data_type)
        sink = self.data_sinks[category]
        output_path = sink.base_path

        print(f"[LOAD] Processor: {data_type} → {category}")
        print(f"[LOAD] Output path: {output_path}")
        print(f"[LOAD] Unique partition combinations: {len(partition_summary)}")
        print(f"[LOAD] Records for {data_type}: {record_count}")

        for row in partition_summary:
            print(f"[LOAD]   - year={row.year} month={row.month} day={row.day} "
                  f"hour={row.hour} min={row.min} => {row['count']} records")

        # Clean sink partitions if requested
        deleted_count = 0
        if clean_sink:
            deleted_count = sink.clean_partitions(output_path, partition_summary, partition_columns)
            print(f"[LOAD] Cleaned {deleted_count} objects from {data_type} partitions")

        # Filter and write
        df_type = out_df.filter(col("data_type") == data_type).drop("data_type")
        output_file_paths, bytes_written = sink.write_json(
            df_type, output_path, partition_columns, row_count_hint=record_count
        )

        print(f"[LOAD] Successfully wrote {record_count} {data_type} records to {output_path}")
        print(f"[LOAD] Wrote {len(output_file_paths)} files ({bytes_written:,} bytes) for {data_type}")

        # Accumulate results
        results.add_category_result(
            category, record_count, len(output_file_paths), len(partition_summary),
            bytes_written, deleted_count, output_file_paths
        )

    def _print_summary(self, results: LoadResults, input_count: int, clean_sink: bool) -> None:
        """Print load operation summary."""
        if results.total_records != input_count:
            print(f"\n[LOAD] WARNING: Total records written ({results.total_records}) != input count ({input_count})")
        else:
            print(f"\n[LOAD] Validation: Total records written matches input count ({results.total_records} records)")

        print(f"\n[LOAD] SUMMARY:")
        print(f"[LOAD]   Total records written: {results.total_records}")
        print(f"[LOAD]   Total files written: {results.total_files}")
        print(f"[LOAD]   Total partitions written: {results.total_partitions}")
        print(f"[LOAD]   Total bytes written: {results.total_bytes:,} ({results.total_bytes / (1024**3):.2f} GB)")

        categories = list(self.data_sinks.keys())
        bytes_summary = ", ".join(f"{cat}={results.bytes_by_category.get(cat, 0):,}" for cat in categories)
        print(f"[LOAD]   Bytes by category: {bytes_summary}")

        if clean_sink:
            print(f"[LOAD]   Total objects cleaned: {results.total_deleted}")

    def _update_metrics(
        self, metrics, results: LoadResults, input_count: int, clean_sink: bool
    ) -> None:
        """Update metrics object with load results."""
        if not metrics:
            return

        categories = list(self.data_sinks.keys())

        # Build output summary
        output_summary = {}
        for category in categories:
            output_summary[category] = {
                "file_count": results.files_by_category.get(category, 0),
                "bytes": results.bytes_by_category.get(category, 0),
                "base_path": self.data_sinks[category].base_path
            }

        metrics.load_records_written = results.total_records
        metrics.load_files_written = results.total_files
        metrics.load_partitions_written = results.total_partitions
        metrics.load_bytes_written = results.total_bytes
        metrics.load_bytes_by_category = results.bytes_by_category
        metrics.load_output_paths = results.output_paths
        metrics.load_output_paths_by_category = results.output_paths_by_category
        metrics.load_output_summary = output_summary

        if clean_sink:
            metrics.load_cleanup_total_deleted = results.total_deleted

        # Common base class fields
        metrics.records_written = results.total_records
        metrics.bytes_written = results.total_bytes

    @staticmethod
    def get_output_schema() -> StructType:
        """Define schema for transformed image JSONL data."""
        return StructType([
            StructField("eventTime", StringType(), False),
            StructField("event_time", StringType(), False),
            StructField("pk", StringType(), False),
            StructField("data", StructType([
                StructField("projectguid", StringType(), False),
                StructField("project_type", StringType(), False),
                StructField("project_subtype", StringType(), True),
                StructField("userid", StringType(), False),
                StructField("inserted", StringType(), False),
                StructField("updated", StringType(), False),
                StructField("product_index", IntegerType(), True),
                StructField("product_type", StringType(), True),
                StructField("productguid", StringType(), True),
                StructField("productimageid", StringType(), True),
                StructField("msp", StringType(), True),
                StructField("mspid", StringType(), True),
                StructField("mediaid", StringType(), True),
                StructField("locationspec", StringType(), True),
            ]), False),
            StructField("5min", IntegerType(), False),
            StructField("year", StringType(), False),
            StructField("month", StringType(), False),
            StructField("day", StringType(), False),
            StructField("hour", StringType(), False),
            StructField("min", StringType(), False),
        ])
