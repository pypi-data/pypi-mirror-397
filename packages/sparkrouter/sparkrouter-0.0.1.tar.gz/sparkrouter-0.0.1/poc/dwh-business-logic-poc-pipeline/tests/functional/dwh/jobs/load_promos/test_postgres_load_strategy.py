import pytest

from dwh.jobs.load_promos.load_promos_job import LoadPromosJob
from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.jobs.load_promos.extract.extract_data_quality_validator import ExtractDataQualityValidator
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.transform.transform_data_quality_validator import TransformDataQualityValidator
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load.new_redshift_loader import NewRedshiftLoader, PostgresLoadStrategy
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from dwh.jobs.load_promos.load.stage_data_quality_validator import StageDataQualityValidator
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder

from dwh.services.notification.notification_service import NoopNotificationService
from dwh.services.data.threshold_evaluator import ThresholdEvaluator

from .test_strategies import (
    FunctionalTestDataSourceStrategy,
    FunctionalValidationDataSourceStrategy,
    FunctionalDeltaDataSinkStrategy,
    FunctionalParquetDataSinkStrategy,
    FunctionalJDBCDataSinkStrategy
)


@pytest.mark.functional
class TestPostgresLoadStrategy:
    """Functional tests for LoadPromosJob with PostgresLoadStrategy - matches integration test configuration"""
    
    def test_postgres_load_strategy_pipeline(self, spark_session, schema_service):
        """Test complete business logic pipeline with PostgresLoadStrategy (same as integration test)"""

        # Create test data using default dates from PromotionDataBuilder
        test_data_builder = (PromotionDataBuilder(schema_service)
                   .with_id("PROMO_TEST_001")
                   .with_name("Business Logic Test Promotion")
                   .with_promotion_type("PERCENTAGE_DISCOUNT")
                   .with_tags("BLACK_FRIDAY", "ELECTRONICS", "SEASONAL", "HIGH_VALUE"))

        # Create Noop backend services
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)

        # Create test strategies
        parquet_source_strategy = FunctionalTestDataSourceStrategy(spark_session, schema_service, "/test/source/path", test_data_builder, debug_schemas=True)
        delta_sink_strategy = FunctionalDeltaDataSinkStrategy(spark_session, schema_service, "/test/unity/path", debug_schemas=True)
        stage_sink_strategy = FunctionalParquetDataSinkStrategy(spark_session, schema_service, "/test/stage/path", debug_schemas=True)
        
        postgres_sink_strategy = FunctionalJDBCDataSinkStrategy(
            spark_session, 
            schema_service, 
            "jdbc:postgresql://test:5432/test", 
            {"user": "test", "password": "test"}, 
            debug_schemas=True
        )
        
        # Create loaders
        unity_loader = UnityLoader(delta_sink_strategy)
        stage_loader = StageLoader(stage_sink_strategy)
        
        # Use PostgresLoadStrategy (same as integration test)
        stage_source_strategy = FunctionalValidationDataSourceStrategy(spark_session, schema_service, "/test/stage/path", stage_sink_strategy)
        postgres_strategy = PostgresLoadStrategy(postgres_sink_strategy, stage_source_strategy)
        postgres_loader = NewRedshiftLoader(postgres_strategy)
        
        # Create DQ validators
        unity_source_strategy = FunctionalValidationDataSourceStrategy(spark_session, schema_service, "/test/unity/path", delta_sink_strategy)
        postgres_source_strategy = FunctionalValidationDataSourceStrategy(spark_session, schema_service, "/test/postgres/path", postgres_sink_strategy)
        
        unity_dq_validator = UnityDataQualityValidator(unity_source_strategy, threshold_evaluator)
        stage_dq_validator = StageDataQualityValidator(stage_source_strategy, threshold_evaluator)
        postgres_dq_validator = RedshiftDataQualityValidator(postgres_source_strategy, threshold_evaluator)
        
        # Create job components
        promotion_extractor = PromotionExtractor(parquet_source_strategy)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        promotion_transformer = PromotionTransformer(schema_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        # Create and execute job
        job = LoadPromosJob(
            notification_service, notification_service,
            promotion_extractor, extract_dq_validator,
            promotion_transformer, transform_dq_validator,
            unity_loader, unity_dq_validator,
            stage_loader, stage_dq_validator,
            postgres_loader, postgres_dq_validator
        )
        
        # Use job execution dates that match the default test data dates (2023-11-24 to 2023-11-27)
        job.execute_job("2023-11-01", "2023-11-30", "functional_test_user")
        
        # Verify business logic executed
        assert len(delta_sink_strategy.written_data) > 0
        assert len(stage_sink_strategy.written_data) > 0
        assert len(postgres_sink_strategy.written_data) > 0
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Unity Data
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        unity_expected_schema = schema_service.get_schema(LoadPromosSchema.UNITY_SCHEMA_REF, LoadPromosSchema.UNITY_TABLE_NAME)
        unity_written_df = spark_session.createDataFrame(delta_sink_strategy.written_data, unity_expected_schema)
        
        unity_actual_columns = set(unity_written_df.columns)
        unity_expected_columns = set([field.name for field in unity_expected_schema.fields])
        assert unity_actual_columns == unity_expected_columns, f"Unity column mismatch. Expected: {unity_expected_columns}, Actual: {unity_actual_columns}"
        
        for expected_field in unity_expected_schema.fields:
            actual_field = unity_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Unity type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Postgres Data
        postgres_expected_schema = schema_service.get_schema(LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF, LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME)
        postgres_written_df = spark_session.createDataFrame(postgres_sink_strategy.written_data, postgres_expected_schema)
        
        postgres_actual_columns = set(postgres_written_df.columns)
        postgres_expected_columns = set([field.name for field in postgres_expected_schema.fields])
        assert postgres_actual_columns == postgres_expected_columns, f"Postgres column mismatch. Expected: {postgres_expected_columns}, Actual: {postgres_actual_columns}"
        
        for expected_field in postgres_expected_schema.fields:
            actual_field = postgres_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Postgres type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify PostgresLoadStrategy behavior - uses DataFrame writes, NOT SQL execution
        assert len(postgres_sink_strategy.executed_sql) == 0, "PostgresLoadStrategy should not execute SQL - it uses DataFrame writes"
        
        # Verify business logic data was written correctly
        postgres_row = postgres_written_df.collect()[0]
        assert postgres_row['promotionid'] == "PROMO_TEST_001"
        assert postgres_row['etl_created_by'] == "functional_test_user"
        
        print("✓ PostgresLoadStrategy functional test passed - matches integration test configuration")