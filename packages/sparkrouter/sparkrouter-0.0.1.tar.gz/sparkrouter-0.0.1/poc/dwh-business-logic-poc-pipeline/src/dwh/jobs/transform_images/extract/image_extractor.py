from datetime import datetime
from pyspark.sql import DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from dwh.jobs.transform_images.extract.spark_s3_data_source import SparkS3DataSource


class ImageExtractor:
    """
    Extracts image data from S3.

    This class handles image-specific concerns:
    - Schema definition for image data
    - Delegating to SparkS3DataSource for partition-aware loading

    Storage concerns (partitioning, paths) are handled by SparkS3DataSource.
    """

    def __init__(self, s3_data_source: SparkS3DataSource):
        self.s3_data_source = s3_data_source

    def extract(self, start_date_utc: datetime, end_date_utc: datetime, metrics=None) -> tuple[DataFrame, DataFrame]:
        """Extract image data from S3 for a date range.

        Args:
            start_date_utc: Start of date range (inclusive)
            end_date_utc: End of date range (exclusive)
            metrics: Optional metrics object to populate

        Returns:
            Tuple of (valid_df, dropped_df)
            - valid_df: Records with valid eventTime and data fields
            - dropped_df: Records that were dropped (corrupt, missing fields)
        """
        schema = ImageExtractor.get_input_schema()
        return self.s3_data_source.read_json_for_date_range(
            start_date_utc, end_date_utc, schema, metrics
        )

    @staticmethod
    def get_input_schema() -> StructType:
        """Define schema for raw image JSONL data"""
        return StructType([
            StructField("eventTime", StringType(), True),
            StructField("event_time", StringType(), True),
            StructField("data", StructType([
                StructField("projectguid", StringType(), True),
                StructField("project_type", StringType(), True),
                StructField("project_subtype", StringType(), True),
                StructField("userid", StringType(), True),
                StructField("inserted", StringType(), True),
                StructField("updated", StringType(), True),
                StructField("state", StringType(), True),
                StructField("product_index", IntegerType(), True),
                StructField("product_type", StringType(), True),
                StructField("productguid", StringType(), True),
                StructField("productimageid", StringType(), True),
                StructField("image_view", StringType(), True),
                StructField("image_id", StringType(), True),
                StructField("image_data", StringType(), True),
            ]), True),
            StructField("__meta__", StructType([
                StructField("framework", StructType([
                    StructField("version", StringType(), True)
                ]), True),
                StructField("savedproject", StructType([
                    StructField("version", StringType(), True),
                    StructField("processor", StringType(), True)
                ]), True)
            ]), True),
            StructField("year", StringType(), True),
            StructField("month", IntegerType(), True),
            StructField("day", IntegerType(), True),
            StructField("hour", IntegerType(), True),
            StructField("5min", IntegerType(), True),
        ])
