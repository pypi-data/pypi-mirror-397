import pytest
from dwh.services.spark.spark_session_factory import SparkSessionFactory


@pytest.mark.functional
class TestSparkSessionFactory:

    def test_create_spark_session_databricks_missing_connection_name_raises_error(self):
        # Arrange
        kwargs = {'service_provider': 'DATABRICKS'}
        # Missing databricks_connection_name

        # Act & Assert
        with pytest.raises(ValueError, match="Missing required argument: databricks_connection_name"):
            SparkSessionFactory.create_spark_session(**kwargs)

    def test_create_spark_session_invalid_service_provider_raises_error(self):
        # Arrange
        kwargs = {'service_provider': 'INVALID'}

        # Act & Assert
        with pytest.raises(ValueError,
                           match="Unsupported spark_service\\[INVALID\\]. Valid options are: DATABRICKS, GLUE, DOCKER"):
            SparkSessionFactory.create_spark_session(**kwargs)

    def test_create_spark_session_none_service_provider_raises_error(self):
        # Arrange
        kwargs = {'service_provider': None}

        # Act & Assert
        with pytest.raises(ValueError,
                           match="Unsupported spark_service\\[None\\]. Valid options are: DATABRICKS, GLUE, DOCKER"):
            SparkSessionFactory.create_spark_session(**kwargs)

    def test_create_spark_session_empty_kwargs_raises_error(self):
        # Arrange
        kwargs = {}  # No service_provider specified

        # Act & Assert
        with pytest.raises(ValueError,
                           match="Unsupported spark_service\\[None\\]. Valid options are: DATABRICKS, GLUE, DOCKER"):
            SparkSessionFactory.create_spark_session(**kwargs)

    def test_create_spark_session_validates_supported_providers(self):
        # Test that supported providers don't raise "Unsupported" errors
        # This test only validates the provider validation logic, not actual Spark session creation
        supported_providers = ['DATABRICKS', 'GLUE', 'CONTAINER']

        for provider in supported_providers:
            kwargs = {'service_provider': provider}
            if provider == 'DATABRICKS':
                kwargs['databricks_connection_name'] = 'test-connection'

            try:
                SparkSessionFactory.create_spark_session(**kwargs)
            except ValueError as e:
                # Should not get "Unsupported spark_service" error for valid providers
                if "Unsupported spark_service" in str(e):
                    pytest.fail(f"Provider {provider} should be supported but got: {e}")
                # Other ValueError exceptions (like missing config) are expected
            except Exception:
                # Other exceptions (like missing dependencies, import errors) are expected in unit tests
                # We only care that the provider validation passes
                pass

    def test_factory_method_exists(self):
        # Test that the factory method exists and is callable
        assert hasattr(SparkSessionFactory, 'create_spark_session')
        assert callable(SparkSessionFactory.create_spark_session)
