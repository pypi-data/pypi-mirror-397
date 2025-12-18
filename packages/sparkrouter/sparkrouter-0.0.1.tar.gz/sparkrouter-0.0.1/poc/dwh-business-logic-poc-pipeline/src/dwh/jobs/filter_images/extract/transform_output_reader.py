"""
Reader for transform_images output.

Reads JSONL text files produced by transform_images job.
Uses ImageLoader schema for validation.
"""
import logging
from typing import Optional
from pyspark.sql import DataFrame, SparkSession
from pyspark.sql.types import StructType

from dwh.jobs.transform_images.load.image_loader import ImageLoader

logger = logging.getLogger(__name__)


class TransformOutputReader:
    """
    Reads transform_images output (JSONL text files).

    transform_images writes partitioned JSONL files using Spark's text writer.
    This reader uses the ImageLoader schema for validation.
    """

    SCHEMA: StructType = ImageLoader.get_output_schema()

    def __init__(self, spark: SparkSession):
        """
        Initialize the reader.

        Args:
            spark: Active SparkSession
        """
        self.spark = spark

    def read(self, path: str) -> DataFrame:
        """
        Read transform_images output from the given path.

        Args:
            path: Path to transform_images output (partitioned JSONL)

        Returns:
            DataFrame with transform_images data

        Raises:
            ValueError: If no data found at path
        """
        logger.info(f"Reading transform_images output (JSONL) from: {path}")

        try:
            df = self.spark.read.schema(self.SCHEMA).json(path)

            # Check if DataFrame has data
            if not df.head(1):
                raise ValueError(f"No data found at transform output path: {path}")

            count = df.count()
            logger.info(f"Read {count:,} records from transform output")

            return df

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Failed to read transform output from {path}: {e}")

    def get_schema(self) -> StructType:
        """Return the expected schema for transform_images output."""
        return self.SCHEMA
