import pytest
from pyspark.sql import Row
from dwh.jobs.load_promos.load.unity_loader import UnityLoader
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from tests.functional.dwh.jobs.load_promos.test_strategies import FunctionalDeltaDataSinkStrategy


@pytest.mark.functional
class TestUnityLoader:
    """Functional tests for UnityLoader"""
    
    def test_unity_loader_writes_to_delta_sink(self, spark_session, schema_service):
        """Test UnityLoader writes data to Delta sink strategy"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("UNITY_TEST_001")
                           .with_name("Unity Loader Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame([Row(**records[0])])
        
        # Transform data to Unity format
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create functional Delta sink strategy
        delta_sink_strategy = FunctionalDeltaDataSinkStrategy(
            spark_session, 
            schema_service, 
            "/test/unity/path", 
            debug_schemas=True
        )
        
        # Create Unity loader
        unity_loader = UnityLoader(delta_sink_strategy)
        
        # Execute load
        unity_loader.load(test_df)
        
        # Verify data was written
        assert len(delta_sink_strategy.written_data) == 1
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        written_df = spark_session.createDataFrame(delta_sink_strategy.written_data, expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(written_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = written_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify data content
        row = delta_sink_strategy.written_data[0]
        assert row['promotionid'] == "UNITY_TEST_001"
        assert row['promotioncode'] == "Unity Loader Test"
        
        print("✓ Unity loader functional test passed")