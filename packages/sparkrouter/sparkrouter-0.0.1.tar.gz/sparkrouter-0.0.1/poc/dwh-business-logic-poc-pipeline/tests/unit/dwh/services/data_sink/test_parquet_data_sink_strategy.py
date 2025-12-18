import pytest
from dwh.services.data_sink.parquet_data_sink_strategy import ParquetDataSinkStrategy
from unit.noops import ValidatingNoopSchemaService, NoopSparkSession


class TestParquetDataSinkStrategy:
    """Unit tests for ParquetDataSinkStrategy"""

    @pytest.fixture
    def schema_service(self):
        return ValidatingNoopSchemaService()

    @pytest.fixture
    def strategy(self, schema_service):
        return ParquetDataSinkStrategy(NoopSparkSession(), schema_service, "s3://test-bucket/path/")

    def test_get_type_returns_parquet(self, strategy):
        """Test that get_type returns PARQUET"""
        assert strategy.get_type() == "PARQUET"

    def test_init_with_valid_parameters(self, schema_service):
        """Test initialization with valid parameters"""
        strategy = ParquetDataSinkStrategy(NoopSparkSession(), schema_service, "s3://test-bucket/path/")
        assert strategy.schema_service is schema_service
        assert strategy.path == "s3://test-bucket/path/"
        assert strategy.debug_schemas == False

    def test_init_with_debug_enabled(self, schema_service):
        """Test initialization with debug enabled"""
        strategy = ParquetDataSinkStrategy(NoopSparkSession(), schema_service, "s3://test-bucket/path/", debug_schemas=True)
        assert strategy.debug_schemas == True