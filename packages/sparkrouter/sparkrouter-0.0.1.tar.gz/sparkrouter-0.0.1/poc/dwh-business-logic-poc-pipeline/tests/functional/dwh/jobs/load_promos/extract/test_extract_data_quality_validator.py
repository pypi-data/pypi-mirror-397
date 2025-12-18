import pytest
from dwh.jobs.load_promos.extract.extract_data_quality_validator import ExtractDataQualityValidator
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.services.data.threshold_evaluator import ThresholdEvaluator
from dwh.services.notification.notification_service import NoopNotificationService


@pytest.mark.functional
class TestExtractDataQualityValidatorFunctional:
    """Functional tests for ExtractDataQualityValidator - test with real data and validation logic"""
    
    def test_validate_with_valid_extracted_data(self, spark_session, schema_service):
        """Test ExtractDataQualityValidator with valid extracted data"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("EXTRACT_DQ_001")
                           .with_name("Extract DQ Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("EXTRACT_VALIDATION", "FUNCTIONAL_TEST"))
        
        # Create DataFrame from test data (simulating extractor output)
        test_records = test_data_builder.to_records()
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        extracted_df = spark_session.createDataFrame(test_records, expected_schema)
        
        # Create validator with real threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        extract_dq_validator.validate(extracted_df)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
    
    def test_validate_with_empty_extracted_data(self, spark_session, schema_service):
        """Test ExtractDataQualityValidator with empty extracted data - should fail as expected"""
        # Create empty DataFrame with proper schema
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        empty_df = spark_session.createDataFrame([], schema)
        
        # Create validator with real threshold evaluator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        
        # Execute validation - should fail for empty data (business rule)
        with pytest.raises(ValueError, match="Extract Data Quality - Row Count failed"):
            extract_dq_validator.validate(empty_df)
    
    def test_validate_checks_required_fields(self, spark_session, schema_service):
        """Test that ExtractDataQualityValidator checks for required fields"""
        # Create test data with all required fields
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("EXTRACT_FIELDS_001")
                           .with_name("Field Validation Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        # Create DataFrame
        test_records = test_data_builder.to_records()
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        extracted_df = spark_session.createDataFrame(test_records, expected_schema)
        
        # Verify required fields are present
        columns = set(extracted_df.columns)
        required_fields = {'_id', 'properties_promotionType', 'ptn_ingress_date'}
        assert required_fields.issubset(columns), f"Missing required fields: {required_fields - columns}"
        
        # Create validator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        extract_dq_validator.validate(extracted_df)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
    
    def test_validate_with_multiple_records(self, spark_session, schema_service):
        """Test ExtractDataQualityValidator with multiple promotion records"""
        # Create multiple test records
        builder1 = (PromotionDataBuilder(schema_service)
                   .with_id("MULTI_001")
                   .with_name("Multi Test 1")
                   .with_promotion_type("PERCENTAGE_DISCOUNT"))
        
        builder2 = (PromotionDataBuilder(schema_service)
                   .with_id("MULTI_002")
                   .with_name("Multi Test 2")
                   .with_promotion_type("BOGO"))
        
        # Combine records
        records1 = builder1.to_records()
        records2 = builder2.to_records()
        all_records = records1 + records2
        
        # Create DataFrame
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        extracted_df = spark_session.createDataFrame(all_records, expected_schema)
        
        # Create validator
        notification_service = NoopNotificationService()
        threshold_evaluator = ThresholdEvaluator(notification_service)
        extract_dq_validator = ExtractDataQualityValidator(threshold_evaluator)
        
        # Execute validation
        extract_dq_validator.validate(extracted_df)
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
        
        # Verify multiple records were processed
        assert extracted_df.count() == 2