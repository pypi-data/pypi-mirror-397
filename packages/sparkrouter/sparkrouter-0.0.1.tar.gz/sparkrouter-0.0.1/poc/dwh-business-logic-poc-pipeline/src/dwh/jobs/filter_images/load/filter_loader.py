"""
Loader for filter_images job.

Writes deduplicated output as PARQUET to S3 with run_id in the path,
enabling easy identification and cleanup of individual runs.

NOTE: filter_images writes parquet for efficient cumulative storage,
unlike transform_images which writes JSONL text files.
Parquet is better for filter_images because:
- Data is read multiple times (cumulative processing)
- External clients need efficient reads
- Compression and columnar storage save space
"""
import logging
from typing import List
from pyspark.sql import DataFrame

from dwh.jobs.filter_images.metrics.job_metrics import FilterImagesJobMetrics

logger = logging.getLogger(__name__)


class FilterLoader:
    """
    Loads filtered and deduplicated data to S3.

    Output is written to a run-specific directory to enable:
    - Easy identification of which run produced which files
    - Clean recovery by deleting failed run directories
    - Manifest-based tracking of output locations
    """

    def __init__(
        self,
        spark,
        max_records_per_file: int = 500000,
        compression: str = "snappy"
    ):
        """
        Initialize the loader.

        Args:
            spark: Active SparkSession
            max_records_per_file: Target records per output file (for repartitioning)
            compression: Parquet compression codec
        """
        self.spark = spark
        self.max_records_per_file = max_records_per_file
        self.compression = compression

    def load(
        self,
        df: DataFrame,
        output_path: str,
        metrics: FilterImagesJobMetrics
    ) -> List[str]:
        """
        Write DataFrame to S3 as parquet files.

        Args:
            df: Deduplicated DataFrame to write
            output_path: Full path including run_id (e.g., s3://bucket/.../filter-xxx/)
            metrics: Metrics collector to update

        Returns:
            List of output file paths
        """
        logger.info(f"Writing filtered output to: {output_path}")

        # Calculate optimal number of partitions
        record_count = df.count()
        num_partitions = max(1, record_count // self.max_records_per_file)
        logger.info(f"Repartitioning to {num_partitions} partitions ({record_count:,} records)")

        # Repartition for optimal file sizes
        df_repartitioned = df.repartition(num_partitions)

        # Write parquet files
        df_repartitioned.write.mode("overwrite").parquet(
            output_path,
            compression=self.compression
        )

        # Get list of written files
        output_files = self._list_output_files(output_path)

        # Calculate bytes written
        bytes_written = self._get_total_bytes(output_path)

        # Update metrics
        metrics.output_path = output_path
        metrics.output_files = output_files
        metrics.bytes_written = bytes_written

        logger.info(f"Wrote {len(output_files)} files, {bytes_written:,} bytes to {output_path}")

        return output_files

    def _list_output_files(self, path: str) -> List[str]:
        """
        List all parquet files in the output path.

        Args:
            path: Output directory path

        Returns:
            List of file names (not full paths)
        """
        try:
            from py4j.java_gateway import java_import
            java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")

            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            hadoop_path = self.spark._jvm.Path(path)
            fs = hadoop_path.getFileSystem(hadoop_conf)

            if not fs.exists(hadoop_path):
                return []

            file_statuses = fs.listStatus(hadoop_path)
            files = []

            for status in file_statuses:
                file_name = status.getPath().getName()
                if file_name.endswith('.parquet'):
                    files.append(file_name)

            return sorted(files)

        except Exception as e:
            logger.warning(f"Could not list output files: {e}")
            return []

    def _get_total_bytes(self, path: str) -> int:
        """
        Get total bytes of all files in the output path.

        Args:
            path: Output directory path

        Returns:
            Total bytes
        """
        try:
            from py4j.java_gateway import java_import
            java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.ContentSummary")

            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            hadoop_path = self.spark._jvm.Path(path)
            fs = hadoop_path.getFileSystem(hadoop_conf)

            if not fs.exists(hadoop_path):
                return 0

            summary = fs.getContentSummary(hadoop_path)
            return summary.getLength()

        except Exception as e:
            logger.warning(f"Could not get total bytes: {e}")
            return 0

    def write_latest(
        self,
        df: DataFrame,
        latest_path: str,
        metrics: FilterImagesJobMetrics
    ) -> None:
        """
        Write DataFrame to the "latest" path for external clients.

        This creates a consistent location that external clients can always
        read from without needing to know specific run IDs.

        Args:
            df: Deduplicated DataFrame to write
            latest_path: Path to "latest" output directory
            metrics: Metrics collector to update
        """
        logger.info(f"Writing to latest output path: {latest_path}")

        # First, delete any existing "latest" directory
        self.delete_output(latest_path)

        # Calculate optimal number of partitions
        record_count = df.count()
        num_partitions = max(1, record_count // self.max_records_per_file)

        # Repartition for optimal file sizes
        df_repartitioned = df.repartition(num_partitions)

        # Write parquet files
        df_repartitioned.write.mode("overwrite").parquet(
            latest_path,
            compression=self.compression
        )

        # Update metrics
        metrics.latest_output_path = latest_path
        logger.info(f"Wrote {record_count:,} records to latest path: {latest_path}")

    def delete_output(self, path: str) -> bool:
        """
        Delete output directory (for cleanup on failure).

        Args:
            path: Path to delete

        Returns:
            True if deleted successfully
        """
        try:
            from py4j.java_gateway import java_import
            java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")

            hadoop_conf = self.spark._jsc.hadoopConfiguration()
            hadoop_path = self.spark._jvm.Path(path)
            fs = hadoop_path.getFileSystem(hadoop_conf)

            if fs.exists(hadoop_path):
                fs.delete(hadoop_path, True)  # True = recursive
                logger.info(f"Deleted output: {path}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete output: {e}")
            return False
