"""
Functional test to validate S3 path compatibility between sink and source strategies.

This test addresses the gap in functional testing where FunctionalValidationDataSourceStrategy
bypasses real S3 operations by reading from memory instead of S3 paths.
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder
from dwh.services.data_sink.parquet_data_sink_strategy import ParquetDataSinkStrategy
from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


@pytest.mark.functional
class TestS3PathCompatibility:
    """Test that sink and source strategies use compatible paths for real file operations"""
    
    def test_parquet_sink_source_path_compatibility(self, spark_session, schema_service):
        """Test that parquet sink writes to a path that parquet source can read from"""
        
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("PROMO_PATH_TEST_001")
                           .with_name("Path Compatibility Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("PATH_TEST"))
        
        # Create temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = f"file://{temp_dir}/staging/"
            
            # Create sink strategy and write data
            sink_strategy = ParquetDataSinkStrategy(
                spark_session, 
                schema_service, 
                base_path,
                debug_schemas=True
            )
            
            # Convert test data to DataFrame and transform it (like the real job does)
            from dwh.data.data_serializer import DataSerializer
            from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
            
            raw_df = DataSerializer.to_dataframe(test_data_builder, spark_session)
            transformer = PromotionTransformer(schema_service, debug_schemas=True)
            transformed_df = transformer.transform(raw_df, "path_compatibility_test")
            
            # Write transformed data using sink strategy
            sink_strategy.write_sink_df(
                transformed_df,
                LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
                LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
                mode="overwrite"
            )
            
            # Create source strategy and read data back
            source_strategy = ParquetDataSourceStrategy(
                spark_session,
                schema_service,
                base_path,
                debug_schemas=True
            )
            
            # Read data using source strategy
            read_df = source_strategy.get_source_df(
                LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
                LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            )
            
            # Validate data was read successfully
            assert read_df.count() > 0, "Source strategy should read data written by sink strategy"
            
            # Validate data content matches
            read_data = read_df.collect()
            assert len(read_data) == 1, "Should read exactly one record"
            
            row = read_data[0]
            assert row.promotionid == "PROMO_PATH_TEST_001", "Data content should match"
            assert row.promotiontype == "PERCENTAGE_DISCOUNT", "Data content should match"
            
            print("✓ S3 Path Compatibility Test PASSED: Sink and source strategies use compatible paths")
    
    def test_directory_vs_file_path_handling(self, spark_session, schema_service):
        """Test that source strategy handles both directory paths and direct file paths correctly"""
        
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("PROMO_PATH_TEST_002")
                           .with_name("Directory vs File Path Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        from dwh.data.data_serializer import DataSerializer
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        
        raw_df = DataSerializer.to_dataframe(test_data_builder, spark_session)
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(raw_df, "directory_vs_file_test")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test 1: Directory path (should append table name)
            directory_path = f"file://{temp_dir}/staging/"
            
            sink_strategy = ParquetDataSinkStrategy(spark_session, schema_service, directory_path)
            sink_strategy.write_sink_df(
                test_df,
                LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
                LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            )
            
            source_strategy = ParquetDataSourceStrategy(spark_session, schema_service, directory_path)
            read_df = source_strategy.get_source_df(
                LoadPromosSchema.REDSHIFT_CORE_SCHEMA_REF,
                LoadPromosSchema.REDSHIFT_CORE_TABLE_NAME,
            )
            
            assert read_df.count() == 1, "Directory path should work with table name appending"
            
            # Test 2: Direct file path (should not append table name)
            direct_file_path = f"file://{temp_dir}/direct_file.parquet"
            raw_df.write.mode("overwrite").parquet(direct_file_path)  # Write raw data, not transformed
            
            source_strategy_direct = ParquetDataSourceStrategy(spark_session, schema_service, direct_file_path)
            read_df_direct = source_strategy_direct.get_source_df(
                LoadPromosSchema.SOURCE_SCHEMA_REF,
                LoadPromosSchema.SOURCE_TABLE_NAME
            )
            
            assert read_df_direct.count() == 1, "Direct file path should work without table name appending"
            
            print("✓ Directory vs File Path Test PASSED: Both path types handled correctly")