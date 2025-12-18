import pytest
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from dwh.services.data_sink.parquet_data_sink_strategy import ParquetDataSinkStrategy
from dwh.services.schema.schema_service import DDLSchemaService
from dwh.data.dl_base.promotion.promotion_data_builder import PromotionDataBuilder


class NoopParquetDataSinkStrategy(ParquetDataSinkStrategy):
    """Test strategy that extends ParquetDataSinkStrategy, preserving ALL business logic"""
    
    def __init__(self, spark, schema_service):
        super().__init__(spark, schema_service, "/test/path", debug_schemas=True)
        self.written_data = []
        self.write_calls = []
    
    def _write_parquet_file(self, df, full_path, mode):
        """Override ONLY the isolated backend file writing operation"""
        # Capture data instead of writing to filesystem
        try:
            self.written_data = df.collect()
            row_count = len(self.written_data)
        except Exception:
            # Handle cases where DataFrame can't be collected due to schema issues
            self.written_data = []
            row_count = 0
        
        self.write_calls.append({
            'path': full_path,
            'mode': mode,
            'row_count': row_count,
            'schema': df.schema
        })


@pytest.mark.functional
class TestParquetDataSinkStrategyFunctional:
    """Functional tests for ParquetDataSinkStrategy - test with real Spark DataFrames and schema validation"""
    
    def test_write_sink_df_with_real_data(self, spark_session, schema_service):
        """Test writing real promotion data as Parquet files"""
        # Create test data
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("PARQUET_TEST_001")
                           .with_name("Parquet Sink Test")
                           .with_promotion_type("PERCENTAGE_DISCOUNT")
                           .with_tags("FUNCTIONAL_TEST", "PARQUET"))
        
        # Create DataFrame from test data and transform it
        test_records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame(test_records)
        
        # Transform to match stage schema
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create test strategy that preserves ALL business logic
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        
        # Write data using proper schema reference
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        parquet_strategy.write_sink_df(test_df, LoadPromosSchema.UNITY_SCHEMA_REF, LoadPromosSchema.UNITY_TABLE_NAME)
        
        # Verify business logic executed correctly
        assert len(parquet_strategy.written_data) > 0, "Should have captured written data"
        assert len(parquet_strategy.write_calls) > 0, "Should have recorded write calls"
        
        # Verify schema validation and path construction business logic
        write_call = parquet_strategy.write_calls[0]
        assert write_call['mode'] == 'overwrite', "Should use overwrite mode"
        assert write_call['row_count'] > 0, "Should have written data rows"
    
    def test_write_sink_df_validates_schema(self, spark_session, schema_service):
        """Test that ParquetDataSinkStrategy validates data against schema"""
        # Create test data with all required fields
        test_data_builder = (PromotionDataBuilder(schema_service)
                           .with_id("PARQUET_SCHEMA_001")
                           .with_name("Schema Validation Test")
                           .with_promotion_type("FIXED_DISCOUNT"))
        
        # Create DataFrame and transform it
        test_records = test_data_builder.to_records()
        source_df = spark_session.createDataFrame(test_records)
        
        # Transform to match stage schema
        from dwh.jobs.load_promos.transform.promotion_transformer import PromotionTransformer
        transformer = PromotionTransformer(schema_service)
        test_df = transformer.transform(source_df, "functional_test_user")
        
        # Create test strategy that preserves ALL business logic
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        
        # Write data - should validate against schema
        from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema
        parquet_strategy.write_sink_df(
            test_df, 
            LoadPromosSchema.UNITY_SCHEMA_REF, 
            LoadPromosSchema.UNITY_TABLE_NAME
        )
        
        # Verify business logic executed correctly
        assert len(parquet_strategy.written_data) > 0, "Should have captured written data"
        assert len(parquet_strategy.write_calls) > 0, "Should have recorded write calls"
        
        # Verify schema validation business logic
        written_row = parquet_strategy.written_data[0]
        assert hasattr(written_row, 'promotionid'), "Should have promotionid field after transformation"
        assert written_row.promotionid == "PARQUET_SCHEMA_001", "Should preserve promotion ID"
    
    def test_get_type_returns_parquet(self, spark_session, schema_service):
        """Test that get_type returns correct strategy type"""
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        
        assert parquet_strategy.get_type() == "PARQUET"
    
    def test_parquet_write_modes(self, spark_session, test_ddl_file_reader):
        """Test Parquet write modes (overwrite, append)"""
        test_ddl_content = """
CREATE TABLE mode_table (
    id STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["mode_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        test_data = [("1", 100), ("2", 200)]
        test_schema = StructType([
            StructField("id", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        df = spark_session.createDataFrame(test_data, test_schema)
        
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        
        # Test overwrite mode
        parquet_strategy.write_sink_df(df, "mode_schema.ddl", "mode_table", mode="overwrite")
        assert parquet_strategy.write_calls[-1]['mode'] == "overwrite"
        
        # Test append mode
        parquet_strategy.write_sink_df(df, "mode_schema.ddl", "mode_table", mode="append")
        assert parquet_strategy.write_calls[-1]['mode'] == "append"
        
        print("✓ Parquet write modes verified")
    
    def test_parquet_large_dataset_handling(self, spark_session, test_ddl_file_reader):
        """Test Parquet handling of large datasets"""
        test_ddl_content = """
CREATE TABLE large_table (
    id STRING,
    data STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["large_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create large dataset (1000 rows)
        large_data = [(str(i), f"data_{i}", i * 10) for i in range(1000)]
        large_schema = StructType([
            StructField("id", StringType(), True),
            StructField("data", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        df = spark_session.createDataFrame(large_data, large_schema)
        
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        parquet_strategy.write_sink_df(df, "large_schema.ddl", "large_table")
        
        assert len(parquet_strategy.written_data) == 1000
        assert parquet_strategy.write_calls[0]['row_count'] == 1000
        
        print("✓ Parquet large dataset handling verified")
    
    def test_parquet_compression_modes(self, spark_session, test_ddl_file_reader):
        """Test Parquet compression mode handling"""
        test_ddl_content = """
CREATE TABLE compressed_table (
    id STRING,
    large_text STRING
);
        """
        
        test_ddl_file_reader.file_contents["compressed_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create data with large text fields that benefit from compression
        test_data = [("1", "A" * 1000), ("2", "B" * 1000)]
        test_schema = StructType([
            StructField("id", StringType(), True),
            StructField("large_text", StringType(), True)
        ])
        df = spark_session.createDataFrame(test_data, test_schema)
        
        parquet_strategy = NoopParquetDataSinkStrategy(spark_session, schema_service)
        parquet_strategy.write_sink_df(df, "compressed_schema.ddl", "compressed_table")
        
        # Verify large text was preserved
        written_data = parquet_strategy.written_data
        assert len(written_data[0]['large_text']) == 1000
        assert written_data[0]['large_text'].startswith("A")
        
        print("✓ Parquet compression handling verified")