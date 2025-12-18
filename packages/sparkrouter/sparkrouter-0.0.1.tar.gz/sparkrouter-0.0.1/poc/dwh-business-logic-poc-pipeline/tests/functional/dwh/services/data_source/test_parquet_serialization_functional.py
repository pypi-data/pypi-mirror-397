import pytest
import tempfile
import os
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from dwh.jobs.load_promos.test_data_generator import LoadPromosTestDataGenerator
from dwh.services.schema.schema_service import DDLSchemaService
from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.jobs.load_promos.load_promos_schema import LoadPromosSchema


@pytest.mark.functional
class TestParquetSerializationFunctional:
    """Focused test for Parquet serialization/deserialization schema compatibility"""
    
    def test_parquet_write_read_schema_compatibility(self, spark_session, test_ddl_file_reader):
        """Test that data can be written to and read from Parquet with schema compatibility"""
        # Create schema service
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Generate test data
        df_original = LoadPromosTestDataGenerator.create_test_data(spark_session, schema_service)
        
        # Write to temporary Parquet file
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_path = os.path.join(temp_dir, "test_data.parquet")
            
            # Write DataFrame to Parquet
            df_original.write.mode("overwrite").parquet(parquet_path)
            
            # Create ParquetDataSourceStrategy to read it back
            parquet_strategy = ParquetDataSourceStrategy(
                spark_session, 
                schema_service, 
                parquet_path
            )
            
            # Read back using the same schema validation that production uses
            df_read_back = parquet_strategy.get_source_df(
                LoadPromosSchema.SOURCE_SCHEMA_REF,
                LoadPromosSchema.SOURCE_TABLE_NAME
            )
            
            # Verify data integrity
            original_count = df_original.count()
            read_back_count = df_read_back.count()
            
            assert original_count == read_back_count, f"Row count mismatch: original={original_count}, read_back={read_back_count}"
            
            # Verify schema compatibility
            original_schema = df_original.schema
            read_back_schema = df_read_back.schema
            
            assert len(original_schema.fields) == len(read_back_schema.fields), "Schema field count mismatch"
            
            # Verify specific problematic field
            original_bundle_field = None
            read_back_bundle_field = None
            
            for field in original_schema.fields:
                if field.name == "bundles_bundleA":
                    original_bundle_field = field
                    break
            
            for field in read_back_schema.fields:
                if field.name == "bundles_bundleA":
                    read_back_bundle_field = field
                    break
            
            assert original_bundle_field is not None, "bundles_bundleA field not found in original schema"
            assert read_back_bundle_field is not None, "bundles_bundleA field not found in read-back schema"
            
            print(f"Original bundles_bundleA type: {original_bundle_field.dataType}")
            print(f"Read-back bundles_bundleA type: {read_back_bundle_field.dataType}")
            
            # This test will fail if there's a serialization issue
            assert str(original_bundle_field.dataType) == str(read_back_bundle_field.dataType), \
                f"bundles_bundleA type mismatch: {original_bundle_field.dataType} vs {read_back_bundle_field.dataType}"
            
            print("✓ Parquet write-read schema compatibility verified")
    
    def test_parquet_complex_type_serialization(self, spark_session, test_ddl_file_reader):
        """Test serialization of complex nested types in Parquet"""
        # Create schema with complex nested types
        test_ddl_content = """
CREATE TABLE complex_serialization_table (
    id STRING,
    nested_struct STRUCT<field1:STRING, field2:INT, field3:ARRAY<STRING>>,
    array_of_structs ARRAY<STRUCT<name:STRING, value:INT>>,
    deep_nested STRUCT<level1:STRUCT<level2:STRUCT<value:STRING>>>
);
        """
        
        test_ddl_file_reader.file_contents["complex_serialization.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create complex test data with explicit schema matching DDL
        from pyspark.sql import Row
        from pyspark.sql.types import StructType, StructField, ArrayType
        
        # Define explicit schema matching DDL expectations
        complex_schema = StructType([
            StructField("id", StringType(), True),
            StructField("nested_struct", StructType([
                StructField("field1", StringType(), True),
                StructField("field2", IntegerType(), True),  # Force INT32
                StructField("field3", ArrayType(StringType(), True), True)
            ]), True),
            StructField("array_of_structs", ArrayType(StructType([
                StructField("name", StringType(), True),
                StructField("value", IntegerType(), True)  # Force INT32
            ]), True), True),
            StructField("deep_nested", StructType([
                StructField("level1", StructType([
                    StructField("level2", StructType([
                        StructField("value", StringType(), True)
                    ]), True)
                ]), True)
            ]), True)
        ])
        
        complex_data = [
            Row(
                id="1",
                nested_struct=Row(field1="test1", field2=100, field3=["a", "b", "c"]),
                array_of_structs=[
                    Row(name="item1", value=10),
                    Row(name="item2", value=20)
                ],
                deep_nested=Row(level1=Row(level2=Row(value="deep_value")))
            )
        ]
        
        df_original = spark_session.createDataFrame(complex_data, complex_schema)
        
        # Write-read roundtrip test
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_path = os.path.join(temp_dir, "complex_test.parquet")
            
            df_original.write.mode("overwrite").parquet(parquet_path)
            
            parquet_strategy = ParquetDataSourceStrategy(
                spark_session, 
                schema_service, 
                parquet_path
            )
            
            df_read_back = parquet_strategy.get_source_df(
                "complex_serialization.ddl",
                "complex_serialization_table"
            )
            
            # Verify complex type preservation
            collected_original = df_original.collect()[0]
            collected_read_back = df_read_back.collect()[0]
            
            assert collected_original.nested_struct.field1 == collected_read_back.nested_struct.field1
            assert collected_original.nested_struct.field3 == collected_read_back.nested_struct.field3
            assert len(collected_original.array_of_structs) == len(collected_read_back.array_of_structs)
            assert collected_original.deep_nested.level1.level2.value == collected_read_back.deep_nested.level1.level2.value
            
            print("✓ Complex type serialization verified")
    
    def test_parquet_null_handling_serialization(self, spark_session, test_ddl_file_reader):
        """Test NULL value handling in Parquet serialization"""
        test_ddl_content = """
CREATE TABLE null_serialization_table (
    id STRING,
    nullable_string STRING,
    nullable_struct STRUCT<field1:STRING, field2:INT>,
    nullable_array ARRAY<STRING>
);
        """
        
        test_ddl_file_reader.file_contents["null_serialization.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        from pyspark.sql import Row
        from pyspark.sql.types import StructType, StructField, ArrayType
        
        # Define explicit schema matching DDL expectations
        null_schema = StructType([
            StructField("id", StringType(), True),
            StructField("nullable_string", StringType(), True),
            StructField("nullable_struct", StructType([
                StructField("field1", StringType(), True),
                StructField("field2", IntegerType(), True)  # Force INT32
            ]), True),
            StructField("nullable_array", ArrayType(StringType(), True), True)
        ])
        
        null_test_data = [
            Row(
                id="1",
                nullable_string=None,
                nullable_struct=None,
                nullable_array=None
            ),
            Row(
                id="2",
                nullable_string="not_null",
                nullable_struct=Row(field1="test", field2=42),
                nullable_array=["item1", "item2"]
            )
        ]
        
        df_original = spark_session.createDataFrame(null_test_data, null_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_path = os.path.join(temp_dir, "null_test.parquet")
            
            df_original.write.mode("overwrite").parquet(parquet_path)
            
            parquet_strategy = ParquetDataSourceStrategy(
                spark_session, 
                schema_service, 
                parquet_path
            )
            
            df_read_back = parquet_strategy.get_source_df(
                "null_serialization.ddl",
                "null_serialization_table"
            )
            
            collected = df_read_back.orderBy("id").collect()
            
            # Verify NULL preservation
            assert collected[0].nullable_string is None
            assert collected[0].nullable_struct is None
            assert collected[0].nullable_array is None
            
            # Verify non-NULL values
            assert collected[1].nullable_string == "not_null"
            assert collected[1].nullable_struct.field1 == "test"
            assert collected[1].nullable_array == ["item1", "item2"]
            
            print("✓ NULL handling in serialization verified")
    
    def test_parquet_large_data_serialization(self, spark_session, test_ddl_file_reader):
        """Test serialization performance with larger datasets"""
        test_ddl_content = """
CREATE TABLE large_serialization_table (
    id STRING,
    data STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["large_serialization.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Generate larger test dataset
        large_test_data = [(str(i), f"data_{i}", i * 10) for i in range(1000)]
        
        df_original = spark_session.createDataFrame(
            large_test_data,
            schema=StructType([
                StructField("id", StringType(), True),
                StructField("data", StringType(), True),
                StructField("value", IntegerType(), True)
            ])
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            parquet_path = os.path.join(temp_dir, "large_test.parquet")
            
            df_original.write.mode("overwrite").parquet(parquet_path)
            
            parquet_strategy = ParquetDataSourceStrategy(
                spark_session, 
                schema_service, 
                parquet_path
            )
            
            df_read_back = parquet_strategy.get_source_df(
                "large_serialization.ddl",
                "large_serialization_table"
            )
            
            # Verify data integrity with larger dataset
            assert df_original.count() == df_read_back.count()
            assert df_original.count() == 1000
            
            # Sample verification
            sample_original = df_original.filter(df_original.id == "500").collect()[0]
            sample_read_back = df_read_back.filter(df_read_back.id == "500").collect()[0]
            
            assert sample_original.data == sample_read_back.data
            assert sample_original.value == sample_read_back.value
            
            print("✓ Large data serialization verified")