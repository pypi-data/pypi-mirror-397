import pytest
import tempfile
import os
from datetime import datetime
from decimal import Decimal
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, TimestampType, 
    BooleanType, DecimalType, ArrayType
)
from pyspark.sql import Row

from dwh.services.data_sink.delta_data_sink_strategy import DeltaDataSinkStrategy
from dwh.services.schema.schema_service import DDLSchemaService


class DeltaDataSinkStrategyForTesting(DeltaDataSinkStrategy):
    """Test implementation extending DeltaDataSinkStrategy for functional testing"""
    
    def __init__(self, spark, schema_service, path: str, debug_schemas: bool = False):
        super().__init__(spark, schema_service, path, debug_schemas)
        self.delta_operations = []
    
    def _write_delta_file(self, df, full_path: str, mode: str) -> None:
        """Override only backend I/O - write as parquet to simulate Delta backend"""
        os.makedirs(full_path, exist_ok=True)
        df.write.mode(mode).parquet(full_path)
        
        # Track Delta operations for testing
        self.delta_operations.append({
            'operation': 'write',
            'path': full_path,
            'mode': mode,
            'row_count': df.count(),
            'schema': df.schema
        })


@pytest.mark.functional
class TestDeltaSinkFunctional:
    """Functional tests for DeltaDataSinkStrategy - test complete business workflows with Noop Delta backend"""
    
    def test_delta_sink_workflow(self, spark_session, test_ddl_file_reader):
        """Test complete Delta sink workflow with schema validation"""
        test_ddl_content = """
CREATE TABLE test_table (
    id STRING,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        test_data = [("1", "test1", 100), ("2", "test2", 200)]
        test_schema = StructType([
            StructField("id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        df = spark_session.createDataFrame(test_data, test_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            strategy.write_sink_df(df, "test_schema.ddl", "test_table")
            
            assert len(strategy.delta_operations) == 1
            assert strategy.delta_operations[0]['row_count'] == 2
            assert os.path.exists(temp_dir)
            
            written_df = spark_session.read.parquet(temp_dir)
            assert written_df.count() == 2
        
        print("✓ Delta sink basic workflow verified")
    
    def test_delta_schema_enforcement_strict(self, spark_session, test_ddl_file_reader):
        """Test strict schema enforcement prevents data corruption"""
        test_ddl_content = """
CREATE TABLE strict_table (
    id STRING,
    amount DECIMAL(10,2),
    created_at TIMESTAMP
);
        """
        
        test_ddl_file_reader.file_contents["strict_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create DataFrame with wrong types
        wrong_data = [("1", "invalid_decimal", "invalid_timestamp")]
        wrong_schema = StructType([
            StructField("id", StringType(), True),
            StructField("amount", StringType(), True),  # Wrong type
            StructField("created_at", StringType(), True)  # Wrong type
        ])
        df = spark_session.createDataFrame(wrong_data, wrong_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            
            with pytest.raises(ValueError, match="SINK SCHEMA MISMATCH"):
                strategy.write_sink_df(df, "strict_schema.ddl", "strict_table")
        
        print("✓ Delta strict schema enforcement verified")
    
    def test_delta_complex_data_types(self, spark_session, test_ddl_file_reader):
        """Test Delta handling of complex nested data types"""
        test_ddl_content = """
CREATE TABLE complex_table (
    id STRING,
    metadata STRUCT<version:INT, created:TIMESTAMP>,
    tags ARRAY<STRING>,
    settings STRUCT<enabled:BOOLEAN, priority:INT>
);
        """
        
        test_ddl_file_reader.file_contents["complex_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create DataFrame with explicit schema to avoid type inference issues
        from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, BooleanType, ArrayType
        
        explicit_schema = StructType([
            StructField("id", StringType(), True),
            StructField("metadata", StructType([
                StructField("version", IntegerType(), True),
                StructField("created", TimestampType(), True)
            ]), True),
            StructField("tags", ArrayType(StringType()), True),
            StructField("settings", StructType([
                StructField("enabled", BooleanType(), True),
                StructField("priority", IntegerType(), True)
            ]), True)
        ])
        
        test_data = [
            ("1", (1, datetime(2024, 1, 1)), ["tag1", "tag2"], (True, 1))
        ]
        df = spark_session.createDataFrame(test_data, explicit_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            strategy.write_sink_df(df, "complex_schema.ddl", "complex_table")
            
            assert len(strategy.delta_operations) == 1
            written_df = spark_session.read.parquet(temp_dir)
            collected = written_df.collect()
            assert collected[0].metadata.version == 1
            assert collected[0].tags == ["tag1", "tag2"]
        
        print("✓ Delta complex data types verified")
    
    def test_delta_null_handling(self, spark_session, test_ddl_file_reader):
        """Test Delta NULL value handling across all types"""
        test_ddl_content = """
CREATE TABLE null_table (
    id STRING,
    nullable_int INT,
    nullable_decimal DECIMAL(10,2),
    nullable_timestamp TIMESTAMP,
    nullable_boolean BOOLEAN
);
        """
        
        test_ddl_file_reader.file_contents["null_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create DataFrame with explicit schema to match DDL exactly
        explicit_schema = StructType([
            StructField("id", StringType(), True),
            StructField("nullable_int", IntegerType(), True),
            StructField("nullable_decimal", DecimalType(10,2), True),
            StructField("nullable_timestamp", TimestampType(), True),
            StructField("nullable_boolean", BooleanType(), True)
        ])
        
        test_data = [
            ("1", None, None, None, None),
            ("2", 42, Decimal('123.45'), datetime(2024, 1, 1), True)
        ]
        df = spark_session.createDataFrame(test_data, explicit_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            strategy.write_sink_df(df, "null_schema.ddl", "null_table")
            
            written_df = spark_session.read.parquet(temp_dir)
            collected = written_df.orderBy("id").collect()
            assert collected[0].nullable_int is None
            assert collected[1].nullable_int == 42
        
        print("✓ Delta NULL handling verified")
    
    def test_delta_write_modes(self, spark_session, test_ddl_file_reader):
        """Test Delta write modes (overwrite, append)"""
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
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            
            # Test overwrite mode
            strategy.write_sink_df(df, "mode_schema.ddl", "mode_table", mode="overwrite")
            assert strategy.delta_operations[-1]['mode'] == "overwrite"
            
            # Test append mode
            strategy.write_sink_df(df, "mode_schema.ddl", "mode_table", mode="append")
            assert strategy.delta_operations[-1]['mode'] == "append"
        
        print("✓ Delta write modes verified")
    
    def test_delta_empty_dataset_handling(self, spark_session, test_ddl_file_reader):
        """Test Delta handling of empty datasets"""
        test_ddl_content = """
CREATE TABLE empty_table (
    id STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["empty_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Create empty DataFrame with correct schema
        empty_schema = StructType([
            StructField("id", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        empty_df = spark_session.createDataFrame([], empty_schema)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            strategy = DeltaDataSinkStrategyForTesting(spark_session, schema_service, temp_dir)
            strategy.write_sink_df(empty_df, "empty_schema.ddl", "empty_table")
            
            assert strategy.delta_operations[0]['row_count'] == 0
            written_df = spark_session.read.parquet(temp_dir)
            assert written_df.count() == 0
        
        print("✓ Delta empty dataset handling verified")
