import pytest
from dwh.jobs.load_promos.transform.transform_data_quality_validator import TransformDataQualityValidator
from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.services.data.threshold_evaluator import ThresholdEvaluator
from dwh.services.notification.notification_service import NoopNotificationService


@pytest.mark.functional
class TestTransformDataQualityValidatorFunctional:
    """Functional tests for TransformDataQualityValidator - test with real data and validation logic"""
    
    def test_validate_with_transformed_data(self, spark_session, schema_service):
        """Test TransformDataQualityValidator with real transformed data"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("TRANSFORM_DQ_001")
                           .with_name("Transform DQ Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("TRANSFORM_VALIDATION", "FUNCTIONAL_TEST"))
        
        # Create and transform data
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        transformer = PromotionTransformer(schema_service)
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
        
        # Create validator with real threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        transform_dq_validator.validate(validated_df)
    
    def test_validate_checks_transformed_schema(self, spark_session, schema_service):
        """Test that TransformDataQualityValidator validates transformed schema"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("SCHEMA_CHECK_001")
                           .with_name("Schema Check Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        # Create and transform data
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        transformer = PromotionTransformer(schema_service)
        transformed_df = transformer.transform(source_df, "schema_test_user")
        
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
        
        # Create validator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        transform_dq_validator.validate(validated_df)
    
    def test_validate_with_empty_transformed_data(self, spark_session, schema_service):
        """Test TransformDataQualityValidator with empty transformed data - should fail as expected"""
        # Create empty DataFrame with proper source schema
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        empty_source_df = spark_session.createDataFrame([], source_schema)
        
        # Transform empty data
        transformer = PromotionTransformer(schema_service)
        transformed_df = transformer.transform(empty_source_df, "empty_test_user")
        
        # Verify empty result
        assert transformed_df.count() == 0
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED (even for empty data)
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
        
        # Create validator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        # Execute validation - should fail for empty data (business rule)
        with pytest.raises(ValueError, match="Transform Data Quality - Row Count failed"):
            transform_dq_validator.validate(validated_df)
    
    def test_validate_checks_business_rule_application(self, spark_session, schema_service):
        """Test that TransformDataQualityValidator verifies business rules were applied"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("BUSINESS_RULE_DQ_001")
                           .with_name("Business Rule DQ Test")
                           .with_promotion_type("BOGO"))
        
        # Create and transform data
        test_records = test_data_builder.to_records()
        source_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        source_df = spark_session.createDataFrame(test_records, source_schema)
        
        transformer = PromotionTransformer(schema_service)
        transformed_df = transformer.transform(source_df, "business_rule_dq_user")
        
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
        
        # Verify business rules were applied correctly
        row = validated_df.collect()[0]
        assert row['promotionid'] == "BUSINESS_RULE_DQ_001"
        assert row['etl_created_by'] == "business_rule_dq_user"
        assert row['dwcreatedby'] == "business_rule_dq_user"
        assert row['uniquepromoflag'] == False
        assert row['prepaidflag'] == False
        
        # Create validator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        transform_dq_validator = TransformDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        transform_dq_validator.validate(validated_df)