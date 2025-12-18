import pytest
from datetime import datetime
from pyspark.sql import Row
from dwh.jobs.load_promos.load.unity_data_quality_validator import UnityDataQualityValidator
from dwh.jobs.load_promos.load.stage_data_quality_validator import StageDataQualityValidator
from dwh.jobs.load_promos.load.redshift_data_quality_validator import RedshiftDataQualityValidator
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.services.data.threshold_evaluator import ThresholdEvaluator
from dwh.services.notification.notification_service import NoopNotificationService
from tests.functional.dwh.jobs.load_promos.test_strategies import (
    FunctionalValidationDataSourceStrategy,
    FunctionalDeltaDataSinkStrategy,
    FunctionalParquetDataSinkStrategy,
    FunctionalJDBCDataSinkStrategy
)


@pytest.mark.functional
class TestDataQualityValidators:
    """Functional tests for all data quality validators"""
    
    def test_unity_data_quality_validator_validates_delta_data(self, spark_session, schema_service):
        """Test UnityDataQualityValidator validates Unity Catalog Delta data"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("UNITY_DQ_001")
                           .with_name("Unity DQ Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create Unity sink and write data
        unity_sink = FunctionalDeltaDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            debug_schemas=True
        )
        
        unity_sink.write_sink_df(
            test_df,
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create Unity source for validation
        unity_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            unity_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create validator
        unity_validator = UnityDataQualityValidator(unity_source, threshold_evaluator)
        
        # Execute validation
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # Should not raise exception for valid data
        unity_validator.validate(start_date, end_date)
        
        print("✓ Unity data quality validator functional test passed")
    
    def test_stage_data_quality_validator_validates_s3_staging_data(self, spark_session, schema_service):
        """Test StageDataQualityValidator validates S3 staging data"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("STAGE_DQ_001")
                           .with_name("Stage DQ Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create staging sink and use StageLoader to handle TIME conversion
        staging_sink = FunctionalParquetDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            debug_schemas=True
        )
        
        # Use StageLoader to convert TIME columns and write to staging
        from dwh.jobs.load_promos.load.stage_loader import StageLoader
        stage_loader = StageLoader(staging_sink)
        stage_loader.load(test_df)
        
        # Create staging source for validation
        staging_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            staging_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create validator
        stage_validator = StageDataQualityValidator(staging_source, threshold_evaluator)
        
        # Execute validation
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # Should not raise exception for valid data
        stage_validator.validate(start_date, end_date)
        
        print("✓ Stage data quality validator functional test passed")
    
    def test_redshift_data_quality_validator_validates_database_data(self, spark_session, schema_service):
        """Test RedshiftDataQualityValidator validates database data"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("REDSHIFT_DQ_001")
                           .with_name("Redshift DQ Test")
                           .with_promotion_type("BOGO"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create database sink and write data
        database_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        database_sink.write_sink_df(
            test_df,
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create database source for validation
        database_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/database/path", 
            database_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create validator
        redshift_validator = RedshiftDataQualityValidator(database_source, threshold_evaluator)
        
        # Execute validation
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # Should not raise exception for valid data
        redshift_validator.validate(start_date, end_date)
        
        print("✓ Redshift data quality validator functional test passed")
    
    def test_validators_fail_on_empty_data(self, spark_session, schema_service):
        """Test all validators fail appropriately on empty data"""
        # Create empty DataFrame with correct schema
        empty_df = spark_session.createDataFrame([], schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF, 
            LoadPromosSchema.UNITY_TABLE_NAME
        ))
        
        # Create sink with empty data
        unity_sink = FunctionalDeltaDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/empty/path", 
            debug_schemas=True
        )
        
        unity_sink.write_sink_df(
            empty_df,
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create source for validation
        unity_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/empty/path", 
            unity_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create validator
        unity_validator = UnityDataQualityValidator(unity_source, threshold_evaluator)
        
        # Execute validation - should raise exception for empty data
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        with pytest.raises(ValueError, match="Unity Data Quality - Row Count failed"):
            unity_validator.validate(start_date, end_date)
        
        print("✓ Data quality validators empty data handling functional test passed")