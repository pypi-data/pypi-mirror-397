import pytest
from datetime import datetime
from dwh.jobs.load_promos.extract.promotion_extractor import PromotionExtractor
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from ..test_strategies import FunctionalTestDataSourceStrategy


@pytest.mark.functional
class TestPromotionExtractorFunctional:
    """Functional tests for PromotionExtractor - test with real Spark DataFrames and business logic"""
    
    def test_extract_reads_source_data(self, spark_session, schema_service):
        """Test that PromotionExtractor reads source data correctly"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("EXTRACT_TEST_001")
                           .with_name("Extractor Test Promotion")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("FUNCTIONAL_TEST", "EXTRACT"))
        
        # Create functional test source strategy
        source_strategy = FunctionalTestDataSourceStrategy(
            spark_session, schema_service, "/test/source/path", test_data_builder, debug_schemas=True
        )
        
        # Create and test extractor
        extractor = PromotionExtractor(source_strategy)
        
        # Execute extraction
        start_date = datetime(2023, 11, 1)
        end_date = datetime(2023, 11, 30)
        extracted_df = extractor.extract(start_date, end_date)
        
        # Verify data was extracted
        assert extracted_df is not None
        assert extracted_df.count() > 0
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
    
    def test_extract_with_date_filtering(self, spark_session, schema_service):
        """Test that PromotionExtractor applies date filtering correctly"""
        # Create test data with specific dates
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("EXTRACT_DATE_001")
                           .with_name("Date Filter Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        # Create functional test source strategy
        source_strategy = FunctionalTestDataSourceStrategy(
            spark_session, schema_service, "/test/source/path", test_data_builder
        )
        
        # Create extractor
        extractor = PromotionExtractor(source_strategy)
        
        # Execute extraction with date range that includes both ptn_ingress_date AND updatedate
        start_date = datetime(2023, 11, 10)  # Before updatedate (2023-11-15) in test data
        end_date = datetime(2023, 11, 30)    # After ptn_ingress_date (2023-11-24) in test data
        extracted_df = extractor.extract(start_date, end_date)
        
        # Verify data was extracted (dates should match promotion schedule)
        assert extracted_df is not None
        assert extracted_df.count() > 0
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"
    
    def test_extract_handles_empty_source(self, spark_session, schema_service):
        """Test that PromotionExtractor handles empty source data"""
        # Create empty test data builder
        empty_builder = PromotionDataBuilder(schema_service)
        # Don't add any records - builder will be empty
        
        # Create functional test source strategy with empty data
        source_strategy = FunctionalTestDataSourceStrategy(
            spark_session, schema_service, "/test/empty/path", empty_builder
        )
        
        # Create extractor
        extractor = PromotionExtractor(source_strategy)
        
        # Execute extraction
        start_date = datetime(2023, 11, 1)
        end_date = datetime(2023, 11, 30)
        extracted_df = extractor.extract(start_date, end_date)
        
        # Verify empty result is handled correctly
        assert extracted_df is not None
        assert extracted_df.count() == 0
        
        # COMPREHENSIVE OUTPUT SCHEMA VALIDATION REQUIRED (even for empty data)
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        expected_schema = schema_service.get_schema(LoadPromosSchema.SOURCE_SCHEMA_REF, LoadPromosSchema.SOURCE_TABLE_NAME)
        
        actual_columns = set(extracted_df.columns)
        expected_columns = set([field.name for field in expected_schema.fields])
        assert actual_columns == expected_columns, f"Column mismatch. Expected: {expected_columns}, Actual: {actual_columns}"
        
        for expected_field in expected_schema.fields:
            actual_field = extracted_df.schema[expected_field.name]
            assert actual_field.dataType == expected_field.dataType, f"Type mismatch for {expected_field.name}: expected {expected_field.dataType}, got {actual_field.dataType}"