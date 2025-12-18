"""
Transformer for filter_images job.

Combines previous filtered output with new transform output
and applies last-duplicate-wins deduplication strategy.

IMPORTANT: When the same image appears in both datasets,
the version from the MORE RECENT transform job is kept.
This is ALWAYS the behavior - no exceptions.
"""
import logging
from typing import Optional, List, Tuple
from pyspark.sql import DataFrame, Window
from pyspark.sql.functions import col, row_number, lit, coalesce

from dwh.jobs.filter_images.metrics.job_metrics import FilterImagesJobMetrics

logger = logging.getLogger(__name__)


class FilterTransformer:
    """
    Transforms and deduplicates filter_images data.

    Strategy: LAST DUPLICATE WINS (ALWAYS)
    - Records are combined from previous filtered output + new transform output
    - Each record is tagged with its source (previous vs new)
    - Duplicates are identified by key columns (e.g., mediaid)
    - When duplicates exist, the record from the MORE RECENT source wins
    - "More recent" is determined by the source_job_timestamp column
    """

    def __init__(
        self,
        dedup_key_columns: List[str],
        dedup_order_column: str,
        source_timestamp_column: str = "_source_job_timestamp"
    ):
        """
        Initialize the transformer.

        Args:
            dedup_key_columns: Columns that uniquely identify a record (e.g., ["mediaid"])
            dedup_order_column: Column to use for ordering within duplicates (e.g., "updated")
            source_timestamp_column: Column name for tracking source job timestamp
        """
        self.dedup_key_columns = dedup_key_columns
        self.dedup_order_column = dedup_order_column
        self.source_timestamp_column = source_timestamp_column

    def transform(
        self,
        previous_df: Optional[DataFrame],
        new_df: DataFrame,
        new_source_timestamp: str,
        metrics: FilterImagesJobMetrics
    ) -> DataFrame:
        """
        Combine and deduplicate data using last-duplicate-wins strategy.

        Args:
            previous_df: Previous filtered output (None if first run of day)
            new_df: New transform output
            new_source_timestamp: ISO timestamp of the new transform job
            metrics: Metrics collector to update

        Returns:
            Deduplicated DataFrame with records from both sources
        """
        # Tag new records with source timestamp
        # This is used for deduplication - more recent timestamps win
        new_tagged = new_df.withColumn(
            self.source_timestamp_column,
            lit(new_source_timestamp)
        )

        if previous_df is None:
            # First run of the day - no deduplication needed
            logger.info("First run of day - no previous data to deduplicate against")
            metrics.records_before_dedup = new_tagged.count()
            metrics.duplicates_removed = 0
            metrics.records_written = metrics.records_before_dedup
            return new_tagged

        # Previous data should already have source timestamp from when it was written
        # If not present, use a very old timestamp so new data wins
        if self.source_timestamp_column not in previous_df.columns:
            previous_tagged = previous_df.withColumn(
                self.source_timestamp_column,
                lit("1970-01-01T00:00:00Z")
            )
            logger.warning(
                f"Previous data missing {self.source_timestamp_column} column - "
                "defaulting to epoch time (new data will win all ties)"
            )
        else:
            previous_tagged = previous_df

        # Combine datasets
        logger.info("Combining previous filtered output with new transform output...")
        combined = previous_tagged.unionByName(new_tagged, allowMissingColumns=True)

        # Count before dedup
        records_before_dedup = combined.count()
        metrics.records_before_dedup = records_before_dedup
        logger.info(f"Combined dataset has {records_before_dedup:,} records before deduplication")

        # Apply last-duplicate-wins deduplication
        logger.info(f"Deduplicating by {self.dedup_key_columns} with last-wins strategy...")
        deduplicated = self._deduplicate_last_wins(combined)

        # Count after dedup
        records_after_dedup = deduplicated.count()
        duplicates_removed = records_before_dedup - records_after_dedup

        metrics.records_written = records_after_dedup
        metrics.duplicates_removed = duplicates_removed

        logger.info(
            f"Deduplication complete: {records_before_dedup:,} -> {records_after_dedup:,} "
            f"({duplicates_removed:,} duplicates removed)"
        )

        return deduplicated

    def _deduplicate_last_wins(self, df: DataFrame) -> DataFrame:
        """
        Apply last-duplicate-wins deduplication.

        For each set of records with matching key columns:
        1. Order by source_timestamp DESC (most recent first)
        2. Then by dedup_order_column DESC (secondary ordering)
        3. Keep only the first record (row_number = 1)

        Args:
            df: Combined DataFrame with duplicates

        Returns:
            Deduplicated DataFrame
        """
        # Create window partitioned by key columns, ordered by timestamp DESC
        window = Window.partitionBy(
            *[col(c) for c in self.dedup_key_columns]
        ).orderBy(
            col(self.source_timestamp_column).desc(),  # Most recent source first
            col(self.dedup_order_column).desc()        # Secondary: most recent record
        )

        # Add row number within each partition
        with_row_num = df.withColumn("_row_num", row_number().over(window))

        # Keep only the first row (most recent) for each key
        deduplicated = with_row_num.filter(col("_row_num") == 1).drop("_row_num")

        return deduplicated

    def get_time_range(
        self,
        df: DataFrame,
        time_column: str
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract min/max timestamps from a DataFrame.

        Args:
            df: DataFrame to analyze
            time_column: Name of the timestamp column

        Returns:
            Tuple of (min_time, max_time) as ISO strings
        """
        if df is None:
            return None, None

        try:
            from pyspark.sql.functions import min as spark_min, max as spark_max

            result = df.select(
                spark_min(time_column).alias("min_time"),
                spark_max(time_column).alias("max_time")
            ).collect()[0]

            min_time = result["min_time"]
            max_time = result["max_time"]

            # Convert to ISO string if timestamps
            if min_time is not None:
                min_time = min_time.isoformat() if hasattr(min_time, 'isoformat') else str(min_time)
            if max_time is not None:
                max_time = max_time.isoformat() if hasattr(max_time, 'isoformat') else str(max_time)

            return min_time, max_time

        except Exception as e:
            logger.warning(f"Could not extract time range: {e}")
            return None, None
