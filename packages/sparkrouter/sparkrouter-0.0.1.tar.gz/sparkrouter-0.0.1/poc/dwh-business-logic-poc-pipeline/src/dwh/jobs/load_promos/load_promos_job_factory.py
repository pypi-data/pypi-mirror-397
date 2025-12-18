from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.load_promos.extract.extract_data_quality_validator import ExtractDataQualityValidator
from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.load.stage_data_quality_validator import StageDataQualityValidator
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from dwh.jobs.load_promos.load.new_redshift_loader import NewRedshiftLoader, RedshiftLoadStrategy, PostgresLoadStrategy
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load_promos_job import LoadPromosJob
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.transform.transform_data_quality_validator import TransformDataQualityValidator
from dwh.services.data.threshold_evaluator import ThresholdEvaluator
from dwh.services.data_sink.data_sink_strategy_factory import DataSinkStrategyFactory
from dwh.services.data_source.data_source_strategy_factory import DataSourceStrategyFactory
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.spark.spark_session_factory import SparkSessionFactory
from dwh.services.schema.schema_service_factory import SchemaServiceFactory


class LoadPromosJobFactory(AbstractJobFactory):
    """
    Factory for LoadPromosJob.

    This job extracts promotion data from S3 parquet files, transforms and validates it
    in-memory, then loads to both Unity Catalog and Redshift with final validation.

    Example Configuration (New Architecture):
    {
        "extractor_config": {
            "strategy": "PARQUET",
            "source_table": "s3a://bucket/path/to/parquet/",
        },
        "unity_loader_config": {
            "strategy": "DELTA",
            "path": "s3a://bucket/unity-catalog/promotions/d_promotion_3_0/"
        },
        "stage_loader_config": {
            "strategy": "PARQUET",
            "path": "s3a://bucket/staging/promotions/"
        },
        "redshift_loader_config": {
            "strategy": "REDSHIFT",
            "jdbc_url": "jdbc:postgresql://localhost:5439/redshift_db",
            "s3_staging_path": "s3a://bucket/staging/promotions/",
            "properties": {
                "user": "redshift_user",
                "password": "redshift_password",
                "driver": "org.postgresql.Driver"
            }
        },
        "job_failed_notifications": {
            "notification_service": "NOOP"
        },
        "job_success_notifications": {
            "notification_service": "NOOP"
        },
        "data_quality_notifications": {
            "notification_service": "NOOP"
        },
        "schema_service": {
            "ddl_reader": "S3",
            "region": "us-east-1",
            "bucket": "code-bucket",
            "prefix": ""
        }
    }

    Architecture Flow:
    1. Extract: S3 Parquet → DataFrame (with date filtering)
    2. Extract DQ: In-memory validation (schema, nulls, required fields)
    3. Transform: Business logic transformation (flattening, deduplication)
    4. Transform DQ: In-memory validation (business rules, duplicates)
    5. Load: Parallel write to Unity Catalog + Redshift (via S3 staging)
    6. Load DQ: Post-load validation (row counts, referential integrity)
    
    Note: Table names, schema references, and staging paths are hardcoded
    in the respective loader classes as job-specific constants.
    """

    def __init__(
            self,
            notification_factory=None,
            spark_factory=None,
            data_source_strategy_factory=None,
            data_sink_strategy_factory=None,
            schema_service_factory=None,
            **kwargs
    ):
        """Initialize with optional factory dependencies."""
        super().__init__(**kwargs)
        # Use injected or default implementations
        self.notification_factory = notification_factory or NotificationServiceFactory
        self.spark_factory = spark_factory or SparkSessionFactory
        self.data_source_strategy_factory = data_source_strategy_factory or DataSourceStrategyFactory
        self.data_sink_strategy_factory = data_sink_strategy_factory or DataSinkStrategyFactory
        self.schema_service_factory = schema_service_factory or SchemaServiceFactory

    def _get_spark_session(self, **kwargs):
        """Create a Spark session if has_spark is True."""
        has_spark = kwargs.get('has_spark', False)
        if isinstance(has_spark, str):
            # Convert string to boolean
            has_spark = has_spark.lower() in ['true', '1', 'yes']

        if has_spark:
            return self.spark_factory.create_spark_session(**kwargs)

        return None

    def create_job(self, **kwargs) -> LoadPromosJob:
        config = self.parse_job_config(job_name='load_promos_job', **kwargs)
        print("Configuration for LoadPromosJob:", config)

        spark = self._get_spark_session(**kwargs)
        if spark is None:
            raise ValueError('load_promos_job requires a spark_session')
        print(f"spark session? {spark is not None}")

        # Create notification services
        alarm_service = self.notification_factory.create_notification_service(config['job_failed_notifications'])
        success_service = self.notification_factory.create_notification_service(config['job_success_notifications'])
        dq_notification_service = self.notification_factory.create_notification_service(
            config['data_quality_notifications'])

        threshold_evaluator = ThresholdEvaluator(dq_notification_service)

        schema_service = self.schema_service_factory.create_schema_service(config['schema_service'])
        
        # Add source_table path to extractor_config for ParquetStrategy
        extractor_config = config['extractor_config'].copy()
        extractor_config['path'] = extractor_config['source_table']
        s3_source_strategy = self.data_source_strategy_factory.create_data_source_strategy(spark, schema_service, extractor_config)

        # Create components
        promotion_extractor = PromotionExtractor(s3_source_strategy)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        promotion_transformer = PromotionTransformer(schema_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)

        unity_sink_strategy = self.data_sink_strategy_factory.create_data_sink_strategy(spark, schema_service, config['unity_loader_config'])
        unity_source_strategy = self.data_source_strategy_factory.create_data_source_strategy(spark, schema_service, config['unity_loader_config'])
        unity_loader = UnityLoader(unity_sink_strategy)
        unity_dq_validator = UnityDataQualityValidator(unity_source_strategy, threshold_evaluator)

        stage_sink_strategy = self.data_sink_strategy_factory.create_data_sink_strategy(spark, schema_service, config['stage_loader_config'])
        stage_source_strategy = self.data_source_strategy_factory.create_data_source_strategy(spark, schema_service, config['stage_loader_config'])
        stage_loader = StageLoader(stage_sink_strategy)
        stage_dq_validator = StageDataQualityValidator(stage_source_strategy, threshold_evaluator)

        redshift_sink_strategy = self.data_sink_strategy_factory.create_data_sink_strategy(spark, schema_service, config['redshift_loader_config'])
        
        # Create appropriate load strategy based on configuration
        redshift_config = config['redshift_loader_config']
        if redshift_config.get('strategy') == 'POSTGRES':
            # For POSTGRES strategy, use PostgresLoadStrategy with stage source (S3 staging)
            redshift_strategy = PostgresLoadStrategy(redshift_sink_strategy, stage_source_strategy)
        else:
            # For REDSHIFT strategy, use RedshiftLoadStrategy with S3 staging
            s3_staging_path = redshift_config.get('s3_staging_path')
            aws_credentials = redshift_config.get('aws_credentials', {})
            redshift_strategy = RedshiftLoadStrategy(redshift_sink_strategy, s3_staging_path, aws_credentials)
        
        redshift_loader = NewRedshiftLoader(redshift_strategy)
        # Create source strategy for reading from the actual database where data was written
        redshift_source_strategy = self.data_source_strategy_factory.create_data_source_strategy(spark, schema_service, config['redshift_loader_config'])
        redshift_dq_validator = RedshiftDataQualityValidator(redshift_source_strategy, threshold_evaluator)
        return LoadPromosJob(
            alarm_service, success_service, promotion_extractor, extract_dq_validator,
            promotion_transformer, transform_dq_validator, unity_loader, unity_dq_validator,
            stage_loader, stage_dq_validator, redshift_loader, redshift_dq_validator
        )


def main(**kwargs):
    """
    Entrypoint for LoadPromos job.
    """
    print(f"load_promos_job_factory kwargs: {kwargs}")

    operator = LoadPromosJobFactory(**kwargs)
    return operator.run(**kwargs)
