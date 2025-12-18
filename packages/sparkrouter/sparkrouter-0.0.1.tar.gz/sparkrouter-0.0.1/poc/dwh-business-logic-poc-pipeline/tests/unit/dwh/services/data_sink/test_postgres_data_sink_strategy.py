"""
Unit tests for PostgresDataSinkStrategy
"""
import pytest
from dwh.services.data_sink.postgres_data_sink_strategy import PostgresDataSinkStrategy


class NoopDataFrame:
    """Noop DataFrame for testing"""
    pass


class NoopSchemaService:
    """Noop schema service for testing"""
    
    def get_schema(self, schema_ref: str, table_name: str):
        return None



class TestPostgresDataSinkStrategy:
    """Unit tests for PostgresDataSinkStrategy - focus on simple, isolated functionality"""

    def test_init(self):
        """Test PostgresDataSinkStrategy initialization"""
        spark = None
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:postgresql://localhost:5432/test"
        properties = {"user": "test", "password": "test"}

        strategy = PostgresDataSinkStrategy(spark, schema_service, jdbc_url, properties)

        assert strategy.spark is spark
        assert strategy.schema_service is schema_service
        assert strategy.jdbc_url == jdbc_url
        assert strategy.properties == properties

    def test_get_type(self):
        """Test get_type returns POSTGRES"""
        spark = None
        schema_service = NoopSchemaService()
        jdbc_url = "jdbc:postgresql://localhost:5432/test"
        properties = {"user": "test", "password": "test"}

        strategy = PostgresDataSinkStrategy(spark, schema_service, jdbc_url, properties)

        assert strategy.get_type() == "POSTGRES"