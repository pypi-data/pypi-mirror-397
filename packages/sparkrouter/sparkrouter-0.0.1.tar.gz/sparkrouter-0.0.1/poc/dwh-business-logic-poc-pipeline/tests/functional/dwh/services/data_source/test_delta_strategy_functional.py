import pytest
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, ArrayType,
    TimestampType, BooleanType, DecimalType
)
from datetime import datetime
from decimal import Decimal

from dwh.services.data_source.delta_data_source_strategy import DeltaDataSourceStrategy
from dwh.services.schema.schema_service import DDLSchemaService


class DeltaDataSourceStrategyForTesting(DeltaDataSourceStrategy):
    """Test implementation extending DeltaDataSourceStrategy for functional testing"""
    
    def _read_delta_data(self) -> DataFrame:
        """Override only backend I/O - return test data matching expected schema structure"""
        # Create test data that will be validated by parent class business logic
        test_data = [("1", "test1", 100), ("2", "test2", 200)]
        test_schema = StructType([
            StructField("id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        return self.spark.createDataFrame(test_data, test_schema)


@pytest.mark.functional
class TestDeltaStrategyFunctional:
    """Functional tests for DeltaDataSourceStrategy - test complete workflows with Noop backend"""
    
    def test_delta_strategy_workflow(self, spark_session, test_ddl_file_reader):
        """Test complete Delta strategy workflow with schema validation"""
        test_ddl_content = """
CREATE TABLE test_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
            
        strategy = DeltaDataSourceStrategyForTesting(spark_session, schema_service, "test://delta/path")
        result_df = strategy.get_source_df("test_schema.ddl", "test_table")

        assert result_df.count() == 2
        assert set(result_df.columns) == {"id", "name", "value"}

        collected = result_df.orderBy("id").collect()
        assert collected[0].id == "1"
        assert collected[0].name == "test1"
        assert collected[0].value == 100
        
        print("✓ Delta strategy basic workflow verified")
    
    def test_schema_enforcement_missing_columns(self, spark_session, test_ddl_file_reader):
        """Test schema enforcement when data is missing required columns"""
        test_ddl_content = """
CREATE TABLE test_table (
    id STRING,
    name STRING,
    value INT,
    required_field STRING
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class DeltaMissingColumnsStrategy(DeltaDataSourceStrategy):
            def _read_delta_data(self) -> DataFrame:
                # Return data missing required_field column
                test_data = [("1", "test1", 100), ("2", "test2", 200)]
                test_schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("value", IntegerType(), True)
                ])
                return self.spark.createDataFrame(test_data, test_schema)
        
        strategy = DeltaMissingColumnsStrategy(spark_session, schema_service, "test://delta/path")
        
        with pytest.raises(Exception) as exc_info:
            strategy.get_source_df("test_schema.ddl", "test_table")
        
        assert "expected 4 fields, got 3 fields" in str(exc_info.value).lower() or "missing" in str(exc_info.value).lower()
        print("✓ Schema enforcement for missing columns verified")
    
    def test_schema_enforcement_type_mismatch(self, spark_session, test_ddl_file_reader):
        """Test schema enforcement when data types don't match"""
        test_ddl_content = """
CREATE TABLE test_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class DeltaTypeMismatchStrategy(DeltaDataSourceStrategy):
            def _read_delta_data(self) -> DataFrame:
                # Return data with wrong type for value field (STRING instead of INT)
                test_data = [("1", "test1", "not_an_int"), ("2", "test2", "also_not_int")]
                test_schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("value", StringType(), True)  # Wrong type
                ])
                return self.spark.createDataFrame(test_data, test_schema)
        
        strategy = DeltaTypeMismatchStrategy(spark_session, schema_service, "test://delta/path")
        
        with pytest.raises(Exception) as exc_info:
            strategy.get_source_df("test_schema.ddl", "test_table")
        
        assert "type" in str(exc_info.value).lower() or "mismatch" in str(exc_info.value).lower()
        print("✓ Schema enforcement for type mismatch verified")
    
    def test_complex_data_types(self, spark_session, test_ddl_file_reader):
        """Test Delta strategy with complex nested data types"""
        test_ddl_content = """
CREATE TABLE complex_table (
    id STRING,
    metadata STRUCT<version:INT, tags:ARRAY<STRING>>,
    timestamps ARRAY<TIMESTAMP>,
    flags STRUCT<active:BOOLEAN, priority:INT>
);
        """
        
        test_ddl_file_reader.file_contents["complex_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class DeltaComplexTypesStrategy(DeltaDataSourceStrategy):
            def _read_delta_data(self) -> DataFrame:
                # Create data with explicit schema to match DDL expectations
                from pyspark.sql.types import StructType, StructField, ArrayType
                from pyspark.sql import Row
                
                # Define exact schema matching DDL
                complex_schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("metadata", StructType([
                        StructField("version", IntegerType(), True),
                        StructField("tags", ArrayType(StringType(), True), True)
                    ]), True),
                    StructField("timestamps", ArrayType(TimestampType(), True), True),
                    StructField("flags", StructType([
                        StructField("active", BooleanType(), True),
                        StructField("priority", IntegerType(), True)
                    ]), True)
                ])
                
                test_data = [
                    Row(
                        id="1",
                        metadata=Row(version=1, tags=["tag1", "tag2"]),
                        timestamps=[datetime(2024, 1, 1), datetime(2024, 1, 2)],
                        flags=Row(active=True, priority=1)
                    ),
                    Row(
                        id="2",
                        metadata=Row(version=2, tags=["tag3"]),
                        timestamps=[datetime(2024, 2, 1)],
                        flags=Row(active=False, priority=2)
                    )
                ]
                return self.spark.createDataFrame(test_data, complex_schema)
        
        strategy = DeltaComplexTypesStrategy(spark_session, schema_service, "test://delta/path")
        result_df = strategy.get_source_df("complex_schema.ddl", "complex_table")
        
        assert result_df.count() == 2
        collected = result_df.collect()
        assert collected[0].metadata.version == 1
        assert collected[0].metadata.tags == ["tag1", "tag2"]
        assert collected[0].flags.active == True
        
        print("✓ Complex data types handling verified")
    
    def test_null_value_handling(self, spark_session, test_ddl_file_reader):
        """Test NULL value handling across different data types"""
        test_ddl_content = """
CREATE TABLE null_test (
    id STRING,
    nullable_string STRING,
    nullable_int INT,
    nullable_timestamp TIMESTAMP,
    nullable_boolean BOOLEAN
);
        """
        
        test_ddl_file_reader.file_contents["null_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class DeltaNullHandlingStrategy(DeltaDataSourceStrategy):
            def _read_delta_data(self) -> DataFrame:
                from pyspark.sql import Row
                from pyspark.sql.types import StructType, StructField
                
                # Define explicit schema to match DDL expectations
                null_schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("nullable_string", StringType(), True),
                    StructField("nullable_int", IntegerType(), True),
                    StructField("nullable_timestamp", TimestampType(), True),
                    StructField("nullable_boolean", BooleanType(), True)
                ])
                
                test_data = [
                    Row(id="1", nullable_string=None, nullable_int=None, 
                         nullable_timestamp=None, nullable_boolean=None),
                    Row(id="2", nullable_string="test", nullable_int=42,
                         nullable_timestamp=datetime(2024, 1, 1), nullable_boolean=True)
                ]
                return self.spark.createDataFrame(test_data, null_schema)
        
        strategy = DeltaNullHandlingStrategy(spark_session, schema_service, "test://delta/path")
        result_df = strategy.get_source_df("null_schema.ddl", "null_test")
        
        assert result_df.count() == 2
        collected = result_df.orderBy("id").collect()
        assert collected[0].nullable_string is None
        assert collected[0].nullable_int is None
        assert collected[1].nullable_string == "test"
        assert collected[1].nullable_int == 42
        
        print("✓ NULL value handling verified")
    
    def test_empty_dataset_handling(self, spark_session, test_ddl_file_reader):
        """Test behavior with empty datasets"""
        test_ddl_content = """
CREATE TABLE empty_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["empty_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class DeltaEmptyDataStrategy(DeltaDataSourceStrategy):
            def _read_delta_data(self) -> DataFrame:
                test_schema = StructType([
                    StructField("id", StringType(), True),
                    StructField("name", StringType(), True),
                    StructField("value", IntegerType(), True)
                ])
                return self.spark.createDataFrame([], test_schema)
        
        strategy = DeltaEmptyDataStrategy(spark_session, schema_service, "test://delta/path")
        result_df = strategy.get_source_df("empty_schema.ddl", "empty_table")
        
        assert result_df.count() == 0
        assert set(result_df.columns) == {"id", "name", "value"}
        
        print("✓ Empty dataset handling verified")
