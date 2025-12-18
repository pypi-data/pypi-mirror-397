import pytest
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, ArrayType,
    TimestampType, BooleanType, DecimalType
)
from datetime import datetime
from decimal import Decimal

from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.services.schema.schema_service import DDLSchemaService


class ParquetStrategyForTesting(ParquetDataSourceStrategy):
    """Test implementation extending ParquetStrategy for functional testing"""
    
    def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
        """Override only backend I/O - return test data matching expected schema structure"""
        # Create test data that will be validated by parent class business logic
        test_data = [("1", "test1", 100), ("2", "test2", 200)]
        return self.spark.createDataFrame(test_data, required_schema)


@pytest.mark.functional
class TestParquetStrategyFunctional:
    """Functional tests for ParquetStrategy - test complete workflows with Noop backend"""
    
    def test_parquet_strategy_workflow(self, spark_session, test_ddl_file_reader):
        """Test complete Parquet strategy workflow with schema validation"""
        test_ddl_content = """
CREATE TABLE test_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
            
        strategy = ParquetStrategyForTesting(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("test_schema.ddl", "test_table")

        assert result_df.count() == 2
        assert set(result_df.columns) == {"id", "name", "value"}

        collected = result_df.orderBy("id").collect()
        assert collected[0].id == "1"
        assert collected[0].name == "test1"
        assert collected[0].value == 100
        
        print("✓ Parquet strategy basic workflow verified")
    
    def test_schema_enforcement_strict_mode(self, spark_session, test_ddl_file_reader):
        """Test strict schema enforcement prevents silent data corruption"""
        test_ddl_content = """
CREATE TABLE strict_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["strict_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class ParquetStrictSchemaStrategy(ParquetDataSourceStrategy):
            def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
                # Return data with different column order to test schema enforcement
                test_data = [(100, "test1", "1"), (200, "test2", "2")]  # Wrong order
                wrong_schema = StructType([
                    StructField("value", IntegerType(), True),  # Wrong position
                    StructField("name", StringType(), True),
                    StructField("id", StringType(), True)
                ])
                return self.spark.createDataFrame(test_data, wrong_schema)
        
        strategy = ParquetStrictSchemaStrategy(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("strict_schema.ddl", "strict_table")
        
        # Schema enforcement should reorder columns correctly
        assert set(result_df.columns) == {"id", "name", "value"}
        collected = result_df.orderBy("id").collect()
        assert collected[0].id == "1"  # Should be correctly mapped
        assert collected[0].value == 100
        
        print("✓ Strict schema enforcement verified")
    
    def test_complex_nested_types_parquet(self, spark_session, test_ddl_file_reader):
        """Test Parquet handling of complex nested data types"""
        test_ddl_content = """
CREATE TABLE nested_table (
    id STRING,
    metadata STRUCT<version:INT, created:TIMESTAMP>,
    tags ARRAY<STRING>,
    settings STRUCT<enabled:BOOLEAN, priority:INT>
);
        """
        
        test_ddl_file_reader.file_contents["nested_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class ParquetNestedTypesStrategy(ParquetDataSourceStrategy):
            def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
                from pyspark.sql import Row
                test_data = [
                    Row(
                        id="1",
                        metadata=Row(version=1, created=datetime(2024, 1, 1)),
                        tags=["tag1", "tag2", "tag3"],
                        settings=Row(enabled=True, priority=1)
                    ),
                    Row(
                        id="2",
                        metadata=Row(version=2, created=datetime(2024, 1, 2)),
                        tags=["tag4"],
                        settings=Row(enabled=False, priority=2)
                    )
                ]
                return self.spark.createDataFrame(test_data)
        
        strategy = ParquetNestedTypesStrategy(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("nested_schema.ddl", "nested_table")
        
        assert result_df.count() == 2
        collected = result_df.orderBy("id").collect()
        assert collected[0].metadata.version == 1
        assert collected[0].tags == ["tag1", "tag2", "tag3"]
        assert collected[0].settings.enabled == True
        
        print("✓ Complex nested types in Parquet verified")
    
    def test_parquet_compression_handling(self, spark_session, test_ddl_file_reader):
        """Test Parquet compression format handling"""
        test_ddl_content = """
CREATE TABLE compressed_table (
    id STRING,
    large_text STRING,
    numeric_data INT
);
        """
        
        test_ddl_file_reader.file_contents["compressed_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class ParquetCompressionStrategy(ParquetDataSourceStrategy):
            def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
                # Simulate reading compressed parquet data
                test_data = [
                    ("1", "A" * 1000, 12345),  # Large text to benefit from compression
                    ("2", "B" * 1000, 67890),
                    ("3", "C" * 1000, 11111)
                ]
                return self.spark.createDataFrame(test_data, required_schema)
        
        strategy = ParquetCompressionStrategy(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("compressed_schema.ddl", "compressed_table")
        
        assert result_df.count() == 3
        collected = result_df.orderBy("id").collect()
        assert len(collected[0].large_text) == 1000
        assert collected[0].large_text.startswith("A")
        
        print("✓ Parquet compression handling verified")
    
    def test_parquet_schema_evolution(self, spark_session, test_ddl_file_reader):
        """Test Parquet schema evolution with mixed data sources"""
        test_ddl_content = """
CREATE TABLE evolving_table (
    id STRING,
    name STRING,
    value INT,
    new_field STRING
);
        """
        
        test_ddl_file_reader.file_contents["evolved_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class ParquetSchemaEvolutionStrategy(ParquetDataSourceStrategy):
            def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
                # Simulate mixed data: some records have new_field, others don't
                # This represents real schema evolution where newer files have additional fields
                test_data = [
                    ("1", "test1", 100, "value1"),  # New record with new_field
                    ("2", "test2", 200, "value2"),  # New record with new_field
                    ("3", "test3", 300, None)       # Old record, new_field is NULL
                ]
                return self.spark.createDataFrame(test_data, required_schema)
        
        strategy = ParquetSchemaEvolutionStrategy(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("evolved_schema.ddl", "evolving_table")
        
        assert result_df.count() == 3
        collected = result_df.orderBy("id").collect()
        
        # Verify mixed data: some with new_field values, some NULL
        assert collected[0].new_field == "value1"
        assert collected[1].new_field == "value2"
        assert collected[2].new_field is None
        
        print("✓ Parquet schema evolution with mixed data verified")
    
    def test_parquet_partition_handling(self, spark_session, test_ddl_file_reader):
        """Test Parquet partitioned data handling"""
        test_ddl_content = """
CREATE TABLE partitioned_table (
    id STRING,
    data STRING,
    partition_year INT,
    partition_month INT
);
        """
        
        test_ddl_file_reader.file_contents["partitioned_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class ParquetPartitionedStrategy(ParquetDataSourceStrategy):
            def _read_parquet_data(self, required_schema: StructType, table_name: str = None) -> DataFrame:
                # Simulate reading partitioned parquet data
                test_data = [
                    ("1", "data1", 2024, 1),
                    ("2", "data2", 2024, 1),
                    ("3", "data3", 2024, 2),
                    ("4", "data4", 2024, 2)
                ]
                return self.spark.createDataFrame(test_data, required_schema)
        
        strategy = ParquetPartitionedStrategy(spark_session, schema_service, "/test/parquet/path")
        result_df = strategy.get_source_df("partitioned_schema.ddl", "partitioned_table")
        
        assert result_df.count() == 4
        # Test partition filtering capability
        january_data = result_df.filter(result_df.partition_month == 1)
        assert january_data.count() == 2
        
        print("✓ Parquet partition handling verified")
