"""
Unit tests for LoadPromosJob parameter validation
"""
import pytest
from dwh.jobs.load_promos.load_promos_job_factory import LoadPromosJobFactory
from unit.noops import (
    NoopSparkFactory,
    NoopNotificationServiceFactory,
    NoopDataSourceStrategyFactory,
    NoopDataSinkStrategyFactory,
    NoopSchemaServiceFactory
)


class TestLoadPromosJobParameterValidation:
    """Unit tests for parameter validation in LoadPromosJob"""

    @pytest.fixture
    def job_factory(self):
        """Create job factory with Noop dependencies"""
        return LoadPromosJobFactory(
            notification_factory=NoopNotificationServiceFactory(),
            spark_factory=NoopSparkFactory(),
            data_source_strategy_factory=NoopDataSourceStrategyFactory(),
            data_sink_strategy_factory=NoopDataSinkStrategyFactory(),
            schema_service_factory=NoopSchemaServiceFactory()
        )

    @pytest.fixture
    def valid_config(self):
        """Valid job configuration for testing"""
        return {
            "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://test/source/"},
            "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test/unity/"},
            "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://test/stage/"},
            "redshift_loader_config": {
                "strategy": "REDSHIFT", 
                "jdbc_url": "jdbc:test", 
                "s3_staging_path": "s3a://test/staging/"
            },
            "job_failed_notifications": {"notification_service": "NOOP"},
            "job_success_notifications": {"notification_service": "NOOP"},
            "data_quality_notifications": {"notification_service": "NOOP"},
            "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
        }

    def test_valid_job_creation(self, job_factory, valid_config):
        """Test job creation with valid configuration"""
        job = job_factory.create_job(
            has_spark=True,
            service_provider='TEST',
            load_promos_job=valid_config
        )
        assert job is not None

    def test_missing_required_config_s3_config(self, job_factory):
        """Test that missing s3_config raises KeyError in factory"""
        invalid_config = {
            "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test/unity/"},
            "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://test/stage/"},
            "redshift_loader_config": {"strategy": "REDSHIFT", "jdbc_url": "jdbc:test", "s3_staging_path": "s3a://test/staging/"},
            "job_failed_notifications": {"notification_service": "NOOP"},
            "job_success_notifications": {"notification_service": "NOOP"},
            "data_quality_notifications": {"notification_service": "NOOP"},
            "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
        }
        
        with pytest.raises(KeyError, match="extractor_config"):
            job_factory.create_job(
                has_spark=True,
                service_provider='TEST',
                load_promos_job=invalid_config
            )

    def test_missing_required_config_unity_config(self, job_factory):
        """Test that missing unity_loader_config raises KeyError in factory"""
        invalid_config = {
            "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://test/source/"},
            "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://test/stage/"},
            "redshift_loader_config": {"strategy": "REDSHIFT", "jdbc_url": "jdbc:test", "s3_staging_path": "s3a://test/staging/"},
            "job_failed_notifications": {"notification_service": "NOOP"},
            "job_success_notifications": {"notification_service": "NOOP"},
            "data_quality_notifications": {"notification_service": "NOOP"},
            "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
        }
        
        with pytest.raises(KeyError, match="unity_loader_config"):
            job_factory.create_job(
                has_spark=True,
                service_provider='TEST',
                load_promos_job=invalid_config
            )

    def test_missing_source_table(self, job_factory):
        """Test that missing source_table raises KeyError in factory"""
        invalid_config = {
            "extractor_config": {"strategy": "PARQUET"},
            "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test/unity/"},
            "stage_loader_config": {"strategy": "PARQUET", "path": "s3a://test/stage/"},
            "redshift_loader_config": {"strategy": "REDSHIFT", "jdbc_url": "jdbc:test", "s3_staging_path": "s3a://test/staging/"},
            "job_failed_notifications": {"notification_service": "NOOP"},
            "job_success_notifications": {"notification_service": "NOOP"},
            "data_quality_notifications": {"notification_service": "NOOP"},
            "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
        }
        
        with pytest.raises(KeyError, match="source_table"):
            job_factory.create_job(
                has_spark=True,
                service_provider='TEST',
                load_promos_job=invalid_config
            )

    def test_no_spark_session_fails(self, job_factory, valid_config):
        """Test that missing spark session raises ValueError"""
        with pytest.raises(ValueError, match="load_promos_job requires a spark_session"):
            job_factory.create_job(
                has_spark=False,
                service_provider='TEST',
                load_promos_job=valid_config
            )

    def test_missing_load_promos_job_config(self, job_factory):
        """Test that missing load_promos_job config raises ValueError"""
        with pytest.raises(ValueError, match="load_promos_job value must be a dict"):
            job_factory.create_job(
                has_spark=True,
                service_provider='TEST'
            )