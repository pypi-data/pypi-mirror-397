from pyspark.sql import DataFrame
from pyspark.sql.functions import col, coalesce, current_timestamp, count as spark_count


class DroppedRecordLoader:
    """
    Loads dropped records to S3 for analysis.

    Storage concerns (partitioning, paths) are handled by SparkS3DataSink.
    """

    def __init__(self, s3_data_sink):
        self.s3_data_sink = s3_data_sink

    def load(self, dropped_dfs: list[DataFrame], metrics=None) -> None:
        """Write dropped records to S3 partitioned by drop phase and time.

        Each DataFrame is written separately since schemas may differ between phases.

        Args:
            dropped_dfs: List of dropped DataFrames from different phases (extract, transform)
            metrics: Optional metrics collector
        """
        # Filter to valid DataFrames
        valid_dfs = [df for df in (dropped_dfs or []) if df is not None]

        if not valid_dfs:
            print("[DROPPED LOAD] No dropped DataFrames to process")
            self._update_metrics(metrics, 0, 0, 0, [], None)
            return

        # Setup partitioning
        time_partition_columns = self.s3_data_sink.get_partition_columns()
        partition_columns = ["drop_phase", "drop_reason"] + time_partition_columns
        output_path = f"{self.s3_data_sink.base_path}/dropped"
        interval = self.s3_data_sink.partition_interval_minutes

        print(f"[DROPPED LOAD] Output path: {output_path}")

        # Process each DataFrame and collect results
        total_records = 0
        total_files = 0
        total_bytes = 0
        all_output_paths = []

        for i, dropped_df in enumerate(valid_dfs):
            result = self._process_batch(
                dropped_df, i, len(valid_dfs),
                partition_columns, output_path, interval
            )
            if result:
                records, files, bytes_written, paths = result
                total_records += records
                total_files += files
                total_bytes += bytes_written
                all_output_paths.extend(paths)

        # Print summary
        if total_records > 0:
            print(f"[DROPPED LOAD] Successfully wrote {total_records} dropped records")
            print(f"[DROPPED LOAD] Wrote {total_files} files ({total_bytes:,} bytes)")
        else:
            print("[DROPPED LOAD] No dropped records to write (all batches empty)")

        # Update metrics once at the end
        self._update_metrics(metrics, total_records, total_files, total_bytes, all_output_paths, output_path)

    def _process_batch(
        self,
        dropped_df: DataFrame,
        batch_index: int,
        total_batches: int,
        partition_columns: list[str],
        output_path: str,
        interval: int
    ) -> tuple[int, int, int, list[str]] | None:
        """Process a single batch of dropped records.

        Returns:
            Tuple of (record_count, file_count, bytes_written, output_paths) or None if empty
        """
        # Add fallback timestamp and partition columns
        df_with_fallback = dropped_df.withColumn(
            "_timestamp_for_partition",
            coalesce(col("eventTime"), current_timestamp().cast("string"))
        )
        df_with_partitions = (
            self.s3_data_sink.add_partition_columns(df_with_fallback, "_timestamp_for_partition")
            .drop("_timestamp_for_partition")
            .drop(f"{interval}min")
        )

        # Single aggregation for partition distribution and count
        partition_summary = df_with_partitions.groupBy(*partition_columns).agg(
            spark_count("*").alias("count")
        ).collect()

        if not partition_summary:
            print(f"[DROPPED LOAD] Batch {batch_index + 1}/{total_batches} is empty, skipping")
            return None

        record_count = sum(row['count'] for row in partition_summary)

        # Log batch details
        print(f"[DROPPED LOAD] Processing batch {batch_index + 1}/{total_batches} with {record_count} records")
        print(f"[DROPPED LOAD] Batch {batch_index + 1} partition combinations: {len(partition_summary)}")
        for row in partition_summary:
            print(f"[DROPPED LOAD]   - {row.drop_phase}/{row.drop_reason} "
                  f"year={row.year} month={row.month} day={row.day} hour={row.hour} min={row.min} "
                  f"=> {row['count']} records")

        # Write data
        output_file_paths, bytes_written = self.s3_data_sink.write_json(
            df_with_partitions,
            output_path,
            partition_columns,
            row_count_hint=record_count
        )

        return record_count, len(output_file_paths), bytes_written, output_file_paths

    def _update_metrics(
        self,
        metrics,
        total_records: int,
        total_files: int,
        total_bytes: int,
        all_output_paths: list[str],
        output_path: str | None
    ) -> None:
        """Update metrics object with dropped record results."""
        if not metrics:
            return

        metrics.load_dropped_records_written = total_records
        metrics.load_dropped_files_written = total_files
        metrics.load_dropped_bytes_written = total_bytes
        metrics.load_dropped_output_paths = all_output_paths

        # Add to category-based metrics (same structure as nautilus/savedproject)
        if total_records > 0:
            metrics.load_bytes_by_category["dropped"] = total_bytes
            metrics.load_output_paths_by_category["dropped"] = all_output_paths
            metrics.load_output_summary["dropped"] = {
                "file_count": total_files,
                "bytes": total_bytes,
                "records": total_records,
                "base_path": output_path
            }
