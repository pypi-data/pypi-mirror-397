from pyspark.sql.types import StructType, StructField, StringType
import logging

from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.transform_images.extract.image_extractor import ImageExtractor
from dwh.jobs.transform_images.extract.spark_s3_data_source import SparkS3DataSource
from dwh.jobs.transform_images.load.image_loader import ImageLoader
from dwh.jobs.transform_images.load.spark_s3_data_sink import SparkS3DataSink
from dwh.jobs.transform_images.load.dropped_record_loader import DroppedRecordLoader
from dwh.jobs.transform_images.transform.image_transformer import ImageTransformer
from dwh.jobs.transform_images.transform_images_job import TransformImagesJob
from dwh.services.spark.spark_session_factory import SparkSessionFactory
from dwh.jobs.transform_images.quality.transform_images_quality_checker import TransformImagesQualityChecker
from dwh.services.event.job_event_publisher_factory import JobEventPublisherFactory


logger = logging.getLogger(__name__)


class TransformImagesJobFactory(AbstractJobFactory):

    def __init__(
            self,
            spark_factory=None,
            **kwargs
    ):
        """Initialize with optional factory dependencies."""
        super().__init__(**kwargs)
        # Use injected or default implementations
        self.spark_factory = spark_factory or SparkSessionFactory

    def _get_spark_session(self, **kwargs):
        """Create a Spark session if has_spark is True."""
        has_spark = kwargs.get('has_spark', False)
        if isinstance(has_spark, str):
            # Convert string to boolean
            has_spark = has_spark.lower() in ['true', '1', 'yes']

        if has_spark:
            return self.spark_factory.create_spark_session(**kwargs)

        return None

    def create_job(self, **kwargs) -> TransformImagesJob:
        config = self.parse_job_config(job_name='transform_images_job', **kwargs)
        print("Configuration for TransformImagesJob:", config)

        spark = self._get_spark_session(**kwargs)
        if spark is None:
            raise ValueError('transform_images_job requires a spark_session')
        print(f"spark session? {spark is not None}")

        # Register the decrypt_and_parse UDF
        # This makes it available for use in SQL queries
        # Register the decrypt_and_parse UDF (same as conftest.py)
        try:
            decrypt_schema = StructType([
                StructField("msp", StringType(), True),
                StructField("mspid", StringType(), True),
                StructField("mediaid", StringType(), True),
                StructField("locationspec", StringType(), True),
            ])

            spark.udf.registerJavaFunction(
                "decrypt_and_parse",
                "com.shutterfly.dwh.udfs.DecryptAndParseUDF",
                decrypt_schema
            )
            logger.info("Successfully registered decrypt_and_parse UDF")
        except Exception as e:
            logger.error(f"Failed to register decrypt_and_parse UDF: {e}")
            raise

        # Create event publisher via factory
        event_publisher_config = config.get('event_publisher_config', {'publisher_type': 'NOOP'})
        event_publisher = JobEventPublisherFactory.create_job_event_publisher(event_publisher_config)

        # Create job-specific quality checker
        quality_checker_config = config.get('quality_checker_config', {})
        quality_checker = TransformImagesQualityChecker(
            drop_rate_yellow=quality_checker_config.get('drop_rate_yellow', 0.05),
            drop_rate_red=quality_checker_config.get('drop_rate_red', 0.10),
            min_records=quality_checker_config.get('min_records', 0)
        )

        # Create data source with path and partition configuration
        extractor_config = config['extractor_config'].copy()
        s3_data_source = SparkS3DataSource(
            spark,
            base_path=extractor_config['path'],
            partition_interval_minutes=extractor_config.get('partition_interval_minutes', 5)
        )
        image_extractor = ImageExtractor(s3_data_source=s3_data_source)

        image_transformer = ImageTransformer()

        # Create data sinks with path and partition configuration
        # Each category gets its own sink with its own output path
        loader_config = config['loader_config'].copy()
        base_path = loader_config['path']
        partition_interval_minutes = loader_config.get('partition_interval_minutes', 5)
        max_records_per_file = loader_config.get('max_records_per_file', 262000)

        # Category resolver: maps data_type value to category name
        def resolve_category(data_type: str) -> str:
            """Map data_type to output category (nautilus or savedproject)."""
            if "nautilus" in data_type.lower():
                return "nautilus"
            return "savedproject"

        # Create a sink for each category with category-specific output path
        data_sinks = {
            "nautilus": SparkS3DataSink(
                spark,
                base_path=f"{base_path}/nautilus/transformed_images",
                partition_interval_minutes=partition_interval_minutes,
                max_records_per_file=max_records_per_file
            ),
            "savedproject": SparkS3DataSink(
                spark,
                base_path=f"{base_path}/savedproject/transformed_images",
                partition_interval_minutes=partition_interval_minutes,
                max_records_per_file=max_records_per_file
            ),
        }
        image_loader = ImageLoader(data_sinks=data_sinks, category_resolver=resolve_category)

        # Create dropped record loader using a separate sink for dropped records
        dropped_sink = SparkS3DataSink(
            spark,
            base_path=base_path,
            partition_interval_minutes=partition_interval_minutes,
            max_records_per_file=max_records_per_file
        )
        dropped_record_loader = DroppedRecordLoader(s3_data_sink=dropped_sink)

        return TransformImagesJob(
            image_extractor=image_extractor,
            image_transformer=image_transformer,
            image_loader=image_loader,
            dropped_record_loader=dropped_record_loader,
            event_publisher=event_publisher,
            quality_checker=quality_checker,
        )

def main(**kwargs):
    """
    Entrypoint for TransformIMages job.
    """
    print(f"Transform_images_job_factory kwargs: {kwargs}")

    operator = TransformImagesJobFactory(**kwargs)
    return operator.run(**kwargs)
