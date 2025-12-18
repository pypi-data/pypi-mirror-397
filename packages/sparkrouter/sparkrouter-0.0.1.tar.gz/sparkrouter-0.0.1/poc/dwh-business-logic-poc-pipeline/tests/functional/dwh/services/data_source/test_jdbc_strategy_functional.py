import pytest
from pyspark.sql import DataFrame
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, 
    TimestampType, BooleanType, DecimalType
)
from datetime import datetime
from decimal import Decimal

from dwh.services.data_source.jdbc_data_source_strategy import JDBCDataSourceStrategy
from dwh.services.schema.schema_service import DDLSchemaService


class JDBCStrategyForTesting(JDBCDataSourceStrategy):
    """Test implementation extending JDBCStrategy for functional testing"""
    
    def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
        """Override only backend I/O - return test data matching expected schema structure"""
        # Create test data that will be validated by parent class business logic
        test_data = [(1, "test1", 100), (2, "test2", 200)]
        test_schema = StructType([
            StructField("id", IntegerType(), False),
            StructField("name", StringType(), True),
            StructField("value", IntegerType(), True)
        ])
        return self.spark.createDataFrame(test_data, test_schema)


@pytest.mark.functional
class TestJDBCStrategyFunctional:
    """Functional tests for JDBCStrategy - test complete workflows with Noop backend"""
    
    def test_jdbc_strategy_workflow(self, spark_session, test_ddl_file_reader):
        """Test complete JDBC strategy workflow with schema validation"""
        test_ddl_content = """
CREATE TABLE test_table (
    id INT NOT NULL,
    name STRING,
    value INT
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
            
        strategy = JDBCStrategyForTesting(spark_session, schema_service, "test://jdbc/test", {})
        result_df = strategy.get_source_df("test_schema.ddl", "test_table")

        assert result_df.count() == 2
        assert set(result_df.columns) == {"id", "name", "value"}

        collected = result_df.orderBy("id").collect()
        assert collected[0].id == 1
        assert collected[0].name == "test1"
        assert collected[0].value == 100
        
        print("✓ JDBC strategy basic workflow verified")
    
    def test_jdbc_connection_parameters_validation(self, spark_session, test_ddl_file_reader):
        """Test JDBC connection parameter validation"""
        test_ddl_content = """
CREATE TABLE test_table (
    id INT,
    name STRING
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        # Test with valid connection parameters
        valid_properties = {
            "user": "test_user",
            "password": "test_password",
            "driver": "org.postgresql.Driver"
        }
        
        class JDBCConnectionTestStrategy(JDBCDataSourceStrategy):
            def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
                # Return data matching exact schema (no extra columns)
                test_data = [(1, "test1"), (2, "test2")]
                test_schema = StructType([
                    StructField("id", IntegerType(), True),
                    StructField("name", StringType(), True)
                ])
                return self.spark.createDataFrame(test_data, test_schema)
        
        strategy = JDBCConnectionTestStrategy(
            spark_session, schema_service, 
            "jdbc:postgresql://localhost:5432/testdb", 
            valid_properties
        )
        
        # Should not raise exception with valid parameters
        result_df = strategy.get_source_df("test_schema.ddl", "test_table")
        assert result_df.count() == 2
        
        print("✓ JDBC connection parameters validation verified")
    
    def test_schema_enforcement_extra_columns(self, spark_session, test_ddl_file_reader):
        """Test schema enforcement when data has extra columns"""
        test_ddl_content = """
CREATE TABLE test_table (
    id INT,
    name STRING
);
        """
        
        test_ddl_file_reader.file_contents["test_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class JDBCExtraColumnsStrategy(JDBCDataSourceStrategy):
            def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
                # Return data with extra column not in schema
                test_data = [(1, "test1", "extra_value"), (2, "test2", "extra_value2")]
                test_schema = StructType([
                    StructField("id", IntegerType(), False),
                    StructField("name", StringType(), True),
                    StructField("extra_column", StringType(), True)  # Extra column
                ])
                return self.spark.createDataFrame(test_data, test_schema)
        
        strategy = JDBCExtraColumnsStrategy(spark_session, schema_service, "test://jdbc/test", {})
        
        # Should detect extra columns and raise validation error
        with pytest.raises(ValueError) as exc_info:
            strategy.get_source_df("test_schema.ddl", "test_table")
        
        assert "unexpected extra fields" in str(exc_info.value).lower()
        
        print("✓ Schema enforcement for extra columns verified")
    
    def test_database_specific_types(self, spark_session, test_ddl_file_reader):
        """Test database-specific data type handling"""
        test_ddl_content = """
CREATE TABLE db_types_table (
    id INT,
    created_at TIMESTAMP,
    is_active BOOLEAN,
    price DECIMAL(10,2),
    start_time TIME
);
        """
        
        test_ddl_file_reader.file_contents["db_types_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class JDBCDatabaseTypesStrategy(JDBCDataSourceStrategy):
            def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
                from pyspark.sql import Row
                from pyspark.sql.types import StructType, StructField
                
                # Define explicit schema matching DDL expectations
                db_types_schema = StructType([
                    StructField("id", IntegerType(), True),
                    StructField("created_at", TimestampType(), True),
                    StructField("is_active", BooleanType(), True),
                    StructField("price", DecimalType(10, 2), True),
                    StructField("start_time", StringType(), True)
                ])
                
                test_data = [
                    Row(
                        id=1,
                        created_at=datetime(2024, 1, 1, 12, 0, 0),
                        is_active=True,
                        price=Decimal('99.99'),
                        start_time="09:30:00"
                    ),
                    Row(
                        id=2,
                        created_at=datetime(2024, 1, 2, 14, 30, 0),
                        is_active=False,
                        price=Decimal('149.50'),
                        start_time="10:15:30"
                    )
                ]
                return self.spark.createDataFrame(test_data, db_types_schema)
        
        strategy = JDBCDatabaseTypesStrategy(spark_session, schema_service, "test://jdbc/test", {})
        result_df = strategy.get_source_df("db_types_schema.ddl", "db_types_table")
        
        assert result_df.count() == 2
        collected = result_df.orderBy("id").collect()
        assert collected[0].is_active == True
        assert str(collected[0].price) == "99.99"
        assert collected[0].start_time == "09:30:00"
        
        print("✓ Database-specific types handling verified")
    
    def test_large_result_set_handling(self, spark_session, test_ddl_file_reader):
        """Test handling of large result sets"""
        test_ddl_content = """
CREATE TABLE large_table (
    id INT,
    data STRING
);
        """
        
        test_ddl_file_reader.file_contents["large_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class JDBCLargeDataStrategy(JDBCDataSourceStrategy):
            def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
                # Simulate large dataset
                test_data = [(i, f"data_{i}") for i in range(1000)]
                test_schema = StructType([
                    StructField("id", IntegerType(), False),
                    StructField("data", StringType(), True)
                ])
                return self.spark.createDataFrame(test_data, test_schema)
        
        strategy = JDBCLargeDataStrategy(spark_session, schema_service, "test://jdbc/test", {})
        result_df = strategy.get_source_df("large_schema.ddl", "large_table")
        
        assert result_df.count() == 1000
        assert set(result_df.columns) == {"id", "data"}
        
        print("✓ Large result set handling verified")
    
    def test_null_constraint_validation(self, spark_session, test_ddl_file_reader):
        """Test NULL constraint validation"""
        test_ddl_content = """
CREATE TABLE constraint_table (
    id INT NOT NULL,
    required_field STRING NOT NULL,
    optional_field STRING
);
        """
        
        test_ddl_file_reader.file_contents["constraint_schema.ddl"] = test_ddl_content
        schema_service = DDLSchemaService(test_ddl_file_reader)
        
        class JDBCNullConstraintStrategy(JDBCDataSourceStrategy):
            def _read_jdbc_data(self, table_name: str, required_schema: StructType) -> DataFrame:
                from pyspark.sql import Row
                from pyspark.sql.types import StructType, StructField
                
                # Define explicit schema matching DDL expectations
                constraint_schema = StructType([
                    StructField("id", IntegerType(), False),  # NOT NULL
                    StructField("required_field", StringType(), False),  # NOT NULL
                    StructField("optional_field", StringType(), True)  # Nullable
                ])
                
                test_data = [
                    Row(id=1, required_field="test1", optional_field=None),
                    Row(id=2, required_field="test2", optional_field="optional")
                ]
                return self.spark.createDataFrame(test_data, constraint_schema)
        
        strategy = JDBCNullConstraintStrategy(spark_session, schema_service, "test://jdbc/test", {})
        result_df = strategy.get_source_df("constraint_schema.ddl", "constraint_table")
        
        assert result_df.count() == 2
        collected = result_df.orderBy("id").collect()
        assert collected[0].required_field == "test1"
        assert collected[0].optional_field is None
        assert collected[1].optional_field == "optional"
        
        print("✓ NULL constraint validation verified")
