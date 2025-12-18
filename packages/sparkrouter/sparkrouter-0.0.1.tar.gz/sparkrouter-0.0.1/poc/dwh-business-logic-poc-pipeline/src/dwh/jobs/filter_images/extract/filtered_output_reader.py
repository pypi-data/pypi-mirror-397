"""
Reader for previous filter_images output.

Reads parquet files produced by earlier filter_images runs.
Uses ImageLoader schema for validation (same schema as transform_images output).
"""
import logging
from typing import Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dwh.jobs.transform_images.load.image_loader import ImageLoader

logger = logging.getLogger(__name__)


class FilteredOutputReader:
    """
    Reads previous filter_images output (parquet files).

    filter_images writes parquet for efficient cumulative storage.
    This reader validates against the same schema as transform_images output.
    """

    SCHEMA: StructType = ImageLoader.get_output_schema()

    def __init__(self, spark: SparkSession):
        """
        Initialize the reader.

        Args:
            spark: Active SparkSession
        """
        self.spark = spark

    def read(self, path: str) -> Optional[DataFrame]:
        """
        Read previous filtered output from the given path.

        Args:
            path: Path to previous filter_images output (parquet)

        Returns:
            DataFrame with previous filtered data, or None if path doesn't exist
        """
        logger.info(f"Reading previous filtered output (parquet) from: {path}")

        try:
            df = self.spark.read.parquet(path)

            # Check if DataFrame has data
            if not df.head(1):
                logger.info(f"No records found at path: {path}")
                return None

            count = df.count()
            logger.info(f"Read {count:,} records from previous filtered output")

            return df

        except Exception as e:
            # Path doesn't exist or other read error - this is expected for first run
            logger.info(f"Could not read previous output from {path}: {e}")
            return None

    def get_schema(self) -> StructType:
        """Return the expected schema for filtered output."""
        return self.SCHEMA
