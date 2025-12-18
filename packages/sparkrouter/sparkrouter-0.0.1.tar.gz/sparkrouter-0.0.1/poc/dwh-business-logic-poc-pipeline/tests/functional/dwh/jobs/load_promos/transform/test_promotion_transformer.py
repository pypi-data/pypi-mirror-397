import pytest
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder


@pytest.mark.functional
class TestPromotionTransformerFunctional:
    """Functional tests for PromotionTransformer - test with real Spark DataFrames and transformation logic"""
    
    def test_transform_flattens_nested_structures(self, spark_session, schema_service):
        """Test that PromotionTransformer flattens nested structures correctly"""
        # Create test data with nested structures
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("TRANSFORM_TEST_001")
                           .with_name("Transform Test Promotion")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("TRANSFORM_TEST", "NESTED_DATA"))
        
        # Create source DataFrame
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        # Create transformer
        transformer = PromotionTransformer(schema_service, debug_schemas=True)
        
        # Execute transformation
        transformed_df = transformer.transform(source_df, "functional_test_user")
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        validated_df = spark_session.createDataFrame(transformed_df.collect(), expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(validated_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = validated_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify business logic was applied
        row = validated_df.collect()[0]
        assert row['promotionid'] == "TRANSFORM_TEST_001"
        assert row['etl_created_by'] == "functional_test_user"
    
    def test_transform_applies_business_rules(self, spark_session, schema_service):
        """Test that PromotionTransformer applies business rules correctly"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("BUSINESS_RULE_001")
                           .with_name("Business Rule Test")
                           .with_promotion_type("FIXED_DISCOUNT")
                           .with_tags("BUSINESS_RULES", "VALIDATION"))
        
        # Create source DataFrame
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        # Create transformer
        transformer = PromotionTransformer(schema_service)
        
        # Execute transformation
        transformed_df = transformer.transform(source_df, "business_rule_user")
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        validated_df = spark_session.createDataFrame(transformed_df.collect(), expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(validated_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = validated_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify business rules were applied
        row = validated_df.collect()[0]
        assert row['uniquepromoflag'] == False
        assert row['prepaidflag'] == False
        assert row['personalizedpromoflag'] == False
        assert row['dwcreatedby'] == "business_rule_user"
        assert row['etl_created_by'] == "business_rule_user"
    
    def test_transform_handles_deduplication(self, spark_session, schema_service):
        """Test that PromotionTransformer handles deduplication correctly"""
        # Create duplicate test data (same ID, different update times)
        builder1 = (PromotionDataBuilder(schema_service)
                   .with_id("DEDUP_001")
                   .with_name("Dedup Test 1")
                   .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        builder2 = (PromotionDataBuilder(schema_service)
                   .with_id("DEDUP_001")  # Same ID
                   .with_name("Dedup Test 2 Updated")
                   .with_promotion_type("FIXED_DISCOUNT"))
        
        # Combine records to create duplicates
        records1 = builder1.to_records()
        records2 = builder2.to_records()
        all_records = records1 + records2
        
        # Create source DataFrame with duplicates
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(all_records, source_schema)
        
        # Verify we have duplicates
        assert source_df.count() == 2
        
        # Create transformer
        transformer = PromotionTransformer(schema_service)
        
        # Execute transformation (should deduplicate)
        transformed_df = transformer.transform(source_df, "dedup_test_user")
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        validated_df = spark_session.createDataFrame(transformed_df.collect(), expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(validated_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = validated_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify deduplication occurred
        assert validated_df.count() == 1
        row = validated_df.collect()[0]
        assert row['promotionid'] == "DEDUP_001"
    
    def test_transform_preserves_data_types(self, spark_session, schema_service):
        """Test that PromotionTransformer preserves correct data types"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("DATATYPE_001")
                           .with_name("Data Type Test")
                           .with_promotion_type("BOGO"))
        
        # Create source DataFrame
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        # Create transformer
        transformer = PromotionTransformer(schema_service)
        
        # Execute transformation
        transformed_df = transformer.transform(source_df, "datatype_test_user")
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        expected_schema = schema_service.get_schema(
            LoadPromosSchema.UNITY_SCHEMA_REF,
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        validated_df = spark_session.createDataFrame(transformed_df.collect(), expected_schema)
        
        # Validate column completeness: all expected columns present, no unexpected columns
        actual_columns = set(validated_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        # Validate data types: each column must have exact expected data type
        for expected_field in expected_schema.fields:
            actual_field = validated_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"