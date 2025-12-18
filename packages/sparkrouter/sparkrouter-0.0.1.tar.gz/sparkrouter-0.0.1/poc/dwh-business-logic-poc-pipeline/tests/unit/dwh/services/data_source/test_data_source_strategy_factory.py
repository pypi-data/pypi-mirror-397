import pytest

from dwh.services.data_source.data_source_strategy_factory import DataSourceStrategyFactory
from dwh.services.data_source.parquet_data_source_strategy import ParquetDataSourceStrategy
from dwh.services.data_source.delta_data_source_strategy import DeltaDataSourceStrategy
from dwh.services.data_source.jdbc_data_source_strategy import JDBCDataSourceStrategy
from pyspark.sql.types import StructType, StringType, StructField
from dwh.services.schema.schema_service import SchemaService
from unit.noops import NoopSparkSession


class NoopSchemaService(SchemaService):
    """Noop schema service for testing"""

    def get_schema(self, schema_ref: str, table_name: str) -> StructType:
        """Return a basic test schema"""
        fields = [
            StructField("_id", StringType(), True),
            StructField("name", StringType(), True),
            StructField("updatedate", StringType(), True),
            StructField("ptn_ingress_date", StringType(), True)
        ]

        print(f"NOOP Schema: Retrieved schema for {table_name} from {schema_ref}")
        return StructType(fields)


class TestDataSourceStrategyFactory:
    """Unit tests for DataSourceStrategyFactory - focus on factory logic only"""
    
    def test_get_service_type_parquet(self):
        """Test service type extraction for PARQUET"""
        config = {"strategy": "PARQUET"}
        result = DataSourceStrategyFactory._get_service_type(config)
        assert result == "PARQUET"
    
    def test_get_service_type_case_insensitive(self):
        """Test service type extraction is case insensitive"""
        config = {"strategy": "parquet"}
        result = DataSourceStrategyFactory._get_service_type(config)
        assert result == "PARQUET"
    
    def test_get_service_type_with_whitespace(self):
        """Test service type extraction handles whitespace"""
        config = {"strategy": "  DELTA  "}
        result = DataSourceStrategyFactory._get_service_type(config)
        assert result == "DELTA"
    
    def test_get_service_type_missing_strategy_raises_error(self):
        """Test error when strategy is missing"""
        config = {}
        with pytest.raises(ValueError, match="Missing strategy. Valid options are: JDBC, PARQUET, DELTA"):
            DataSourceStrategyFactory._get_service_type(config)
    
    def test_get_service_type_none_strategy_raises_error(self):
        """Test error when strategy is None"""
        config = {"strategy": None}
        with pytest.raises(ValueError, match="Missing strategy. Valid options are: JDBC, PARQUET, DELTA"):
            DataSourceStrategyFactory._get_service_type(config)
    
    def test_create_parquet_strategy_returns_correct_type(self):
        """Test that PARQUET strategy creates ParquetStrategy"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        config = {"strategy": "PARQUET", "path": "s3a://bucket/path"}
        
        result = DataSourceStrategyFactory.create_data_source_strategy(spark, schema_service, config)
        assert isinstance(result, ParquetDataSourceStrategy)
    
    def test_create_delta_strategy_returns_correct_type(self):
        """Test that DELTA strategy creates DeltaDataSourceStrategy"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        config = {"strategy": "DELTA", "path": "s3a://bucket/path"}
        
        result = DataSourceStrategyFactory.create_data_source_strategy(spark, schema_service, config)
        assert isinstance(result, DeltaDataSourceStrategy)
    
    def test_create_jdbc_strategy_returns_correct_type(self):
        """Test that JDBC strategy creates JDBCStrategy"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        config = {"strategy": "JDBC", "jdbc_url": "jdbc:test"}
        
        result = DataSourceStrategyFactory.create_data_source_strategy(spark, schema_service, config)
        assert isinstance(result, JDBCDataSourceStrategy)
    
    def test_create_strategy_unsupported_type_raises_error(self):
        """Test error for unsupported strategy type"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        config = {"strategy": "UNSUPPORTED"}
        
        with pytest.raises(ValueError, match="Unsupported strategy"):
            DataSourceStrategyFactory.create_data_source_strategy(spark, schema_service, config)
    
    def test_create_parquet_strategy_missing_path_raises_error(self):
        """Test error when required path is missing for PARQUET"""
        spark = NoopSparkSession()
        schema_service = NoopSchemaService()
        config = {"strategy": "PARQUET"}
        
        with pytest.raises(KeyError, match="path"):
            DataSourceStrategyFactory.create_data_source_strategy(spark, schema_service, config)
    
    def test_valid_types_constant(self):
        """Test that valid_types constant is correct"""
        expected_types = ['JDBC', 'PARQUET', 'DELTA']
        assert DataSourceStrategyFactory.valid_types == expected_types
