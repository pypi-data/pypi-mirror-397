import pytest
from pyspark.sql import Row
from dwh.jobs.load_promos.load.stage_loader import StageLoader
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from tests.functional.dwh.jobs.load_promos.test_strategies import FunctionalParquetDataSinkStrategy


@pytest.mark.functional
class TestStageLoader:
    """Functional tests for StageLoader"""
    
    def test_stage_loader_converts_time_columns_and_writes_to_s3(self, spark_session, schema_service):
        """Test StageLoader converts TIME columns from Unity format to database format"""
        # Create test data with TIME fields in Unity format (seconds)
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("STAGE_TEST_001")
                           .with_name("Stage Loader Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Verify original data has TIME fields as seconds
        original_row = source_df.collect()[0]
        assert original_row['schedule_dailyStartTime'] == 0  # Unity format: seconds as long
        assert original_row['schedule_dailyEndTime'] == 86399  # Unity format: seconds as long
        
        # Transform data to Unity format first
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "test_user")
        
        # Create functional S3 sink strategy
        s3_sink_strategy = FunctionalParquetDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            debug_schemas=True
        )
        
        # Create stage loader
        stage_loader = StageLoader(s3_sink_strategy)
        
        # Execute load
        stage_loader.load(test_df)
        
        # Verify data was written
        assert len(s3_sink_strategy.written_data) == 1
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        written_df = spark_session.createDataFrame(s3_sink_strategy.written_data, expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(written_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify TIME columns were converted from Unity format to database format
        converted_row = s3_sink_strategy.written_data[0]
        assert converted_row['dailystarttime'] == "00:00:00"
        assert converted_row['dailyendtime'] == "23:59:59"
        assert converted_row['promotionid'] == "STAGE_TEST_001"
        assert converted_row['promotioncode'] == "Stage Loader Test"
        
        print("✓ Stage loader TIME conversion functional test passed")
    
    def test_stage_loader_handles_non_numeric_time_values(self, spark_session, schema_service):
        """Test StageLoader handles non-numeric TIME values correctly"""
        # Create test data with non-numeric TIME values
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("STAGE_TEST_002")
                           .with_name("Non-numeric Time Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format first
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "test_user")
        
        # Manually modify TIME columns to have non-numeric values
        from pyspark.sql.functions import lit
        modified_df = test_df.withColumn("dailystarttime", lit("08:30:00")) \
                            .withColumn("dailyendtime", lit("17:30:00"))
        
        # Create functional S3 sink strategy
        s3_sink_strategy = FunctionalParquetDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/staging/path", 
            debug_schemas=True
        )
        
        # Create stage loader
        stage_loader = StageLoader(s3_sink_strategy)
        
        # Execute load
        stage_loader.load(modified_df)
        
        # Verify data was written
        assert len(s3_sink_strategy.written_data) == 1
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
            LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME
        )
        written_df = spark_session.createDataFrame(s3_sink_strategy.written_data, expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(written_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify non-numeric TIME values are preserved unchanged
        converted_row = s3_sink_strategy.written_data[0]
        assert converted_row['dailystarttime'] == "08:30:00"
        assert converted_row['dailyendtime'] == "17:30:00"
        
        print("✓ Stage loader non-numeric TIME handling functional test passed")