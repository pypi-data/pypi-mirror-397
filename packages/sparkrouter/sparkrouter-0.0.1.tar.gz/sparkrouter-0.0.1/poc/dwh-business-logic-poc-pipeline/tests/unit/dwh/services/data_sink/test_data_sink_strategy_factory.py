import pytest
from pyspark.sql.types import StructType, StructField, StringType

from dwh.services.data_sink.data_sink_strategy_factory import DataSinkStrategyFactory
from dwh.services.data_sink.delta_data_sink_strategy import DeltaDataSinkStrategy
from dwh.services.data_sink.postgres_data_sink_strategy import PostgresDataSinkStrategy
from dwh.services.data_sink.redshift_data_sink_strategy import RedshiftDataSinkStrategy
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

class TestDataSinkStrategyFactory:
    """Unit tests for DataSinkStrategyFactory - focus on factory logic only"""
    
    def test_get_service_type_delta(self):
        """Test service type extraction for DELTA"""
        config = {"strategy": "DELTA"}
        result = DataSinkStrategyFactory._get_service_type(config)
        assert result == "DELTA"
    
    def test_get_service_type_case_insensitive(self):
        """Test service type extraction is case insensitive"""
        config = {"strategy": "postgres"}
        result = DataSinkStrategyFactory._get_service_type(config)
        assert result == "POSTGRES"
    
    def test_get_service_type_with_whitespace(self):
        """Test service type extraction handles whitespace"""
        config = {"strategy": "  DELTA  "}
        result = DataSinkStrategyFactory._get_service_type(config)
        assert result == "DELTA"
    
    def test_get_service_type_missing_strategy_raises_error(self):
        """Test error when strategy is missing"""
        config = {}
        with pytest.raises(ValueError, match="Missing strategy. Valid options are: DELTA, PARQUET, REDSHIFT, POSTGRES"):
            DataSinkStrategyFactory._get_service_type(config)
    
    def test_get_service_type_none_strategy_raises_error(self):
        """Test error when strategy is None"""
        config = {"strategy": None}
        with pytest.raises(ValueError, match="Missing strategy. Valid options are: DELTA, PARQUET, REDSHIFT, POSTGRES"):
            DataSinkStrategyFactory._get_service_type(config)
    
    def test_create_delta_strategy_returns_correct_type(self, spark_session):
        """Test that DELTA strategy creates DeltaDataSinkStrategy"""
        schema_service = NoopSchemaService()
        config = {"strategy": "DELTA", "path": "s3a://bucket/path"}
        
        result = DataSinkStrategyFactory.create_data_sink_strategy(spark_session, schema_service, config)
        assert isinstance(result, DeltaDataSinkStrategy)
    
    def test_create_postgres_strategy_returns_correct_type(self, spark_session):
        """Test that POSTGRES strategy creates PostgresDataSinkStrategy"""
        schema_service = NoopSchemaService()
        config = {"strategy": "POSTGRES", "jdbc_url": "jdbc:postgresql://test", "properties": {"user": "test"}}
        
        result = DataSinkStrategyFactory.create_data_sink_strategy(spark_session, schema_service, config)
        assert isinstance(result, PostgresDataSinkStrategy)
    
    def test_create_redshift_strategy_returns_correct_type(self, spark_session):
        """Test that REDSHIFT strategy creates RedshiftDataSinkStrategy"""
        schema_service = NoopSchemaService()
        config = {"strategy": "REDSHIFT", "jdbc_url": "jdbc:redshift://test", "s3_staging_path": "s3://test/"}
        
        result = DataSinkStrategyFactory.create_data_sink_strategy(spark_session, schema_service, config)
        assert isinstance(result, RedshiftDataSinkStrategy)
    
    def test_create_strategy_unsupported_type_raises_error(self, spark_session):
        """Test error for unsupported strategy type"""
        schema_service = NoopSchemaService()
        config = {"strategy": "UNSUPPORTED"}
        
        with pytest.raises(ValueError, match="Unsupported strategy"):
            DataSinkStrategyFactory.create_data_sink_strategy(spark_session, schema_service, config)
    
    def test_create_delta_strategy_missing_path_raises_error(self, spark_session):
        """Test error when required path is missing for DELTA"""
        schema_service = NoopSchemaService()
        config = {"strategy": "DELTA"}
        
        with pytest.raises(KeyError, match="path"):
            DataSinkStrategyFactory.create_data_sink_strategy(spark_session, schema_service, config)
    
    def test_valid_types_constant(self):
        """Test that valid_types constant is correct"""
        expected_types = ['DELTA', 'PARQUET', 'REDSHIFT', 'POSTGRES']
        assert DataSinkStrategyFactory.valid_types == expected_types
