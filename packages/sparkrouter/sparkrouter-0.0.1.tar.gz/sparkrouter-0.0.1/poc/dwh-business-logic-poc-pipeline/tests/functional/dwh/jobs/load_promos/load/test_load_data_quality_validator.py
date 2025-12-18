import pytest
from pyspark.sql import Row
from pyspark.sql import Row
from datetime import datetime
from dwh.jobs.load_promos.load.load_data_quality_validator import LoadDataQualityValidator
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.services.data.threshold_evaluator import ThresholdEvaluator
from dwh.services.notification.notification_service import NoopNotificationService
from tests.functional.dwh.jobs.load_promos.test_strategies import (
    FunctionalValidationDataSourceStrategy,
    FunctionalDeltaDataSinkStrategy,
    FunctionalJDBCDataSinkStrategy
)


@pytest.mark.functional
class TestLoadDataQualityValidator:
    """Functional tests for LoadDataQualityValidator - cross-destination validation"""
    
    def test_load_data_quality_validator_validates_consistency_between_unity_and_redshift(self, spark_session, schema_service):
        """Test LoadDataQualityValidator validates data consistency between Unity and Redshift"""
        # Create identical test data for both destinations
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("LOAD_DQ_001")
                           .with_name("Load DQ Test")
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
        
        # Create Redshift sink and write same data
        redshift_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        redshift_sink.write_sink_df(
            test_df,
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create source strategies for validation
        unity_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            unity_sink
        )
        
        redshift_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/redshift/path", 
            redshift_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create cross-destination validator
        load_validator = LoadDataQualityValidator(
            unity_source, 
            redshift_source, 
            threshold_evaluator
        )
        
        # Execute validation
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Unity Data
        unity_expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        unity_written_df = spark_session.createDataFrame(unity_sink.written_data, unity_expected_schema)
        
        # Validate Unity output schema
        unity_actual_columns = set(unity_written_df.columns)
        unity_expected_columns = set([field.name for field in unity_expected_schema.fields])
        assert unity_actual_columns == unity_expected_columns, f"Unity column mismatch. Expected: {unity_expected_columns}, Actual: {unity_actual_columns}"
        
        for expected_field in unity_expected_schema.fields:
            actual_field = unity_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Unity type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Redshift Data
        redshift_expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        redshift_written_df = spark_session.createDataFrame(redshift_sink.written_data, redshift_expected_schema)
        
        # Validate Redshift output schema
        redshift_actual_columns = set(redshift_written_df.columns)
        redshift_expected_columns = set([field.name for field in redshift_expected_schema.fields])
        assert redshift_actual_columns == redshift_expected_columns, f"Redshift column mismatch. Expected: {redshift_expected_columns}, Actual: {redshift_actual_columns}"
        
        for expected_field in redshift_expected_schema.fields:
            actual_field = redshift_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Redshift type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Should not raise exception for consistent data
        load_validator.validate(start_date, end_date)
        
        print("✓ Load data quality validator consistency functional test passed")
    
    def test_load_data_quality_validator_fails_on_inconsistent_row_counts(self, spark_session, schema_service):
        """Test LoadDataQualityValidator fails when Unity and Redshift have different row counts"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("LOAD_DQ_002")
                           .with_name("Inconsistent Count Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create Unity sink with full data
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
        
        # Create Redshift sink with empty data (simulating inconsistency)
        empty_df = spark_session.createDataFrame([], test_df.schema)
        
        redshift_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        redshift_sink.write_sink_df(
            empty_df,
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create source strategies for validation
        unity_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            unity_sink
        )
        
        redshift_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/redshift/path", 
            redshift_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create cross-destination validator
        load_validator = LoadDataQualityValidator(
            unity_source, 
            redshift_source, 
            threshold_evaluator
        )
        
        # Execute validation - should fail due to inconsistent counts
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Unity Data
        unity_expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        unity_written_df = spark_session.createDataFrame(unity_sink.written_data, unity_expected_schema)
        
        # Validate Unity output schema
        unity_actual_columns = set(unity_written_df.columns)
        unity_expected_columns = set([field.name for field in unity_expected_schema.fields])
        assert unity_actual_columns == unity_expected_columns, f"Unity column mismatch. Expected: {unity_expected_columns}, Actual: {unity_actual_columns}"
        
        for expected_field in unity_expected_schema.fields:
            actual_field = unity_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Unity type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Redshift Data (empty)
        redshift_expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        redshift_written_df = spark_session.createDataFrame(redshift_sink.written_data, redshift_expected_schema)
        
        # Validate Redshift output schema (even though empty)
        redshift_actual_columns = set(redshift_written_df.columns)
        redshift_expected_columns = set([field.name for field in redshift_expected_schema.fields])
        assert redshift_actual_columns == redshift_expected_columns, f"Redshift column mismatch. Expected: {redshift_expected_columns}, Actual: {redshift_actual_columns}"
        
        for expected_field in redshift_expected_schema.fields:
            actual_field = redshift_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Redshift type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        with pytest.raises(ValueError, match="Load Data Quality - Redshift Count failed"):
            load_validator.validate(start_date, end_date)
        
        print("✓ Load data quality validator inconsistency detection functional test passed")
    
    def test_load_data_quality_validator_fails_on_empty_unity_data(self, spark_session, schema_service):
        """Test LoadDataQualityValidator fails when Unity has no data"""
        # Create empty DataFrame with correct schema
        empty_df = spark_session.createDataFrame([], schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF, 
            LoadPromosSchema.UNITY_TABLE_NAME
        ))
        
        # Create Unity sink with empty data
        unity_sink = FunctionalDeltaDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            debug_schemas=True
        )
        
        unity_sink.write_sink_df(
            empty_df,
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create Redshift sink with empty data too
        redshift_sink = FunctionalJDBCDataSinkStrategy(
            spark_session,
            schema_service,
            "jdbc:postgresql://test:5432/test",
            {"user": "test", "password": "test"},
            debug_schemas=True
        )
        
        redshift_sink.write_sink_df(
            empty_df,
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            mode="overwrite"
        )
        
        # Create source strategies for validation
        unity_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            unity_sink
        )
        
        redshift_source = FunctionalValidationDataSourceStrategy(
            spark_session, 
            schema_service, 
            "/test/redshift/path", 
            redshift_sink
        )
        
        # Create threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        
        # Create cross-destination validator
        load_validator = LoadDataQualityValidator(
            unity_source, 
            redshift_source, 
            threshold_evaluator
        )
        
        # Execute validation - should fail due to empty Unity data
        start_date = datetime(2023, 11, 24)
        end_date = datetime(2023, 11, 27)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Unity Data (empty)
        unity_expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        unity_written_df = spark_session.createDataFrame(unity_sink.written_data, unity_expected_schema)
        
        # Validate Unity output schema (even though empty)
        unity_actual_columns = set(unity_written_df.columns)
        unity_expected_columns = set([field.name for field in unity_expected_schema.fields])
        assert unity_actual_columns == unity_expected_columns, f"Unity column mismatch. Expected: {unity_expected_columns}, Actual: {unity_actual_columns}"
        
        for expected_field in unity_expected_schema.fields:
            actual_field = unity_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Unity type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED - Redshift Data (empty)
        redshift_expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        redshift_written_df = spark_session.createDataFrame(redshift_sink.written_data, redshift_expected_schema)
        
        # Validate Redshift output schema (even though empty)
        redshift_actual_columns = set(redshift_written_df.columns)
        redshift_expected_columns = set([field.name for field in redshift_expected_schema.fields])
        assert redshift_actual_columns == redshift_expected_columns, f"Redshift column mismatch. Expected: {redshift_expected_columns}, Actual: {redshift_actual_columns}"
        
        for expected_field in redshift_expected_schema.fields:
            actual_field = redshift_written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Redshift type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        with pytest.raises(ValueError, match="Load Data Quality - Unity Count"):
            load_validator.validate(start_date, end_date)
        
        print("✓ Load data quality validator empty data detection functional test passed")