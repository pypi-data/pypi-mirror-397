import pytest
from dwh.jobs.load_promos.load_promos_job_factory import LoadPromosJobFactory
from dwh.jobs.load_promos.load_promos_job import LoadPromosJob
from dwh.services.data_sink.data_sink_strategy_factory import DataSinkStrategyFactory
from dwh.services.data_source.data_source_strategy_factory import DataSourceStrategyFactory
from unit.noops import (
    NoopSparkFactory,
    NoopSparkSession,
    NoopNotificationServiceFactory,
    NoopSchemaServiceFactory
)


class TestLoadPromosJobFactory:
    """Unit tests for LoadPromosJobFactory - focus on simple, isolated functionality"""

    def test_init_with_factories(self):
        """Test factory initialization with injected dependencies"""
        notification_factory = NoopNotificationServiceFactory()
        spark_factory = NoopSparkFactory()
        data_source_factory = DataSourceStrategyFactory()
        data_sink_factory = DataSinkStrategyFactory()
        schema_factory = NoopSchemaServiceFactory()

        factory = LoadPromosJobFactory(
            notification_factory=notification_factory,
            spark_factory=spark_factory,
            data_source_strategy_factory=data_source_factory,
            data_sink_strategy_factory=data_sink_factory,
            schema_service_factory=schema_factory
        )

        assert factory.notification_factory is notification_factory
        assert factory.spark_factory is spark_factory
        assert factory.data_source_strategy_factory is data_source_factory
        assert factory.data_sink_strategy_factory is data_sink_factory
        assert factory.schema_service_factory is schema_factory

    def test_get_spark_session_string_to_bool_conversion(self):
        """Test string to boolean conversion for has_spark parameter"""
        factory = LoadPromosJobFactory(spark_factory=NoopSparkFactory())

        # Test various string to boolean conversions
        test_cases = [
            ('true', True), ('false', False),
            ('1', True), ('0', False),
            ('yes', True), ('no', False),
            (True, True), (False, False)
        ]

        for input_val, expected in test_cases:
            spark_session = factory._get_spark_session(has_spark=input_val)
            if expected:
                assert spark_session is not None
                assert isinstance(spark_session, NoopSparkSession)
            else:
                assert spark_session is None

    def test_create_job_with_valid_config(self):
        """Test that create_job returns a LoadPromosJob instance with valid config"""
        factory = LoadPromosJobFactory(
            notification_factory=NoopNotificationServiceFactory(),
            spark_factory=NoopSparkFactory(),
            data_source_strategy_factory=DataSourceStrategyFactory(),
            data_sink_strategy_factory=DataSinkStrategyFactory(),
            schema_service_factory=NoopSchemaServiceFactory()
        )

        # Valid config with supported strategies
        job = factory.create_job(
            has_spark=True,
            service_provider='TEST',
            load_promos_job={
                "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://test/source/"},
                "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test/unity/"},
                "stage_loader_config": {"strategy": "DELTA", "path": "s3a://test/stage/"},
                "redshift_loader_config": {"strategy": "POSTGRES", "jdbc_url": "jdbc:test", "properties": {}},
                "job_failed_notifications": {"notification_service": "NOOP"},
                "job_success_notifications": {"notification_service": "NOOP"},
                "data_quality_notifications": {"notification_service": "NOOP"},
                "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
            }
        )

        # Verify job was created with correct type
        assert job is not None
        assert isinstance(job, LoadPromosJob)

    def test_create_job_invalid_stage_strategy_fails(self):
        """Test that invalid stage_loader_config strategy raises ValueError"""
        factory = LoadPromosJobFactory(
            notification_factory=NoopNotificationServiceFactory(),
            spark_factory=NoopSparkFactory(),
            data_source_strategy_factory=DataSourceStrategyFactory(),
            data_sink_strategy_factory=DataSinkStrategyFactory(),
            schema_service_factory=NoopSchemaServiceFactory()
        )

        # Invalid config with unsupported INVALID strategy for stage_loader
        with pytest.raises(ValueError, match="Unsupported strategy\[INVALID\]"):
            factory.create_job(
                has_spark=True,
                service_provider='TEST',
                load_promos_job={
                    "extractor_config": {"strategy": "PARQUET", "source_table": "s3a://test/source/"},
                    "unity_loader_config": {"strategy": "DELTA", "path": "s3a://test/unity/"},
                    "stage_loader_config": {"strategy": "INVALID", "path": "s3a://test/stage/"},
                    "redshift_loader_config": {"strategy": "POSTGRES", "jdbc_url": "jdbc:test", "properties": {}},
                    "job_failed_notifications": {"notification_service": "NOOP"},
                    "job_success_notifications": {"notification_service": "NOOP"},
                    "data_quality_notifications": {"notification_service": "NOOP"},
                    "schema_service": {"ddl_reader": "FS", "base_path": "/test"}
                }
            )
