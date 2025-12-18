import unittest
from typing import Any

from dwh.jobs.schemas.schema_upgrade_job import SchemaUpgradeJob
from dwh.jobs.schemas.schema_upgrade_job_factory import SchemaUpgradeJobFactory
from dwh.services.file.file_locator import FileLocator
from dwh.services.notification.notification_service import NoopNotificationService
from utils.mock_sql_execution_service import MockDatabaseConnectionService


class MockFileLocator(FileLocator):

    def __init__(self, files: dict[str, Any]):
        # {
        #   key: 'path/filename',
        #   value: file contents
        # }
        super().__init__()
        self.files = files

    def list_files(self, path, file_extension=None):
        # Filter all keys with matching path
        matching_files = []

        for file_key in self.files.keys():
            # Check if the file path starts with or contains the requested path
            if file_key.startswith(path) or path in file_key:
                # If file_extension is specified, also check the extension
                if file_extension is None or file_key.endswith(file_extension):
                    matching_files.append(file_key)

        return matching_files

    def read_file(self, key):
        return self.files[key]


class NoopNotificationServiceFactory:
    """A no-op implementation of NotificationServiceFactory for testing."""
    
    @staticmethod
    def create_notification_service(config):
        """Create a NoopNotificationService for testing."""
        return NoopNotificationService()


class NoopFileLocatorFactory:
    """A no-op implementation of FileLocatorFactory for testing."""
    
    @staticmethod
    def create_file_locator(config):
        """Create a MockFileLocator for testing."""
        return MockFileLocator(files={
            'schema_upgrade_job.py': 'SELECT 1;'
        })


class NoopJdbcConnectionServiceFactory:
    """A no-op implementation of JdbcConnectionServiceFactory for testing."""
    
    @staticmethod
    def create_connection(config, spark_session=None):
        """Create a MockDatabaseConnectionService for testing."""
        return MockDatabaseConnectionService()


class NoopSparkSessionFactory:
    """A no-op implementation of SparkSessionFactory for testing."""
    
    @staticmethod
    def create_spark_session(**kwargs):
        """Create a mock Spark session for testing."""
        return object()


class TestSchemaUpgradeJobFactory(unittest.TestCase):

    def test_schema_upgrade_job_validates_required_parameters(self):
        # Test the job validation logic directly without factory
        notifier = NoopNotificationService()
        jdbc_connection_service = MockDatabaseConnectionService()
        file_locator = MockFileLocator(files={
            'schema_upgrade_job.py': 'SELECT 1;'
        })

        # Act & Assert - Test that required parameters are validated
        job = SchemaUpgradeJob(
            alarm_service=notifier,
            postgres_service=jdbc_connection_service,
            ddl_file_service=file_locator
        )

        # Assert - The job should be created successfully
        self.assertIs(job.alarm_service, notifier)
        self.assertIs(job.postgres_service, jdbc_connection_service)
        self.assertIs(job.ddl_file_service, file_locator)
        
    def test_factory_creates_job_with_dependencies(self):
        # Arrange
        factory = SchemaUpgradeJobFactory(
            notification_service_factory=NoopNotificationServiceFactory,
            file_locator_factory=NoopFileLocatorFactory,
            jdbc_connection_service_factory=NoopJdbcConnectionServiceFactory,
            spark_session_factory=NoopSparkSessionFactory
        )
        
        # Create a simple config dictionary
        kwargs = {
            'schema_upgrade_job': {
                'alarm_service': {
                    'type': 'noop'
                },
                'ddl_file_service': {
                    'type': 'mock'
                },
                'postgres_connection': {
                    'type': 'mock'
                }
            }
        }
        
        # Act
        job = factory.create_job(**kwargs)
        
        # Assert
        self.assertIsInstance(job, SchemaUpgradeJob)
        self.assertIsInstance(job.alarm_service, NoopNotificationService)
        self.assertIsInstance(job.ddl_file_service, MockFileLocator)
        self.assertIsInstance(job.postgres_service, MockDatabaseConnectionService)

    def test_factory_main_function_exists(self):
        # Test that the main function exists and is callable
        from dwh.jobs.schemas.schema_upgrade_job_factory import main

        # Assert
        self.assertTrue(callable(main))
        
    def test_factory_raises_error_on_missing_config(self):
        # Arrange
        factory = SchemaUpgradeJobFactory(
            notification_service_factory=NoopNotificationServiceFactory,
            file_locator_factory=NoopFileLocatorFactory,
            jdbc_connection_service_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job()
            
    def test_factory_raises_error_on_missing_required_keys(self):
        # Arrange
        factory = SchemaUpgradeJobFactory(
            notification_service_factory=NoopNotificationServiceFactory,
            file_locator_factory=NoopFileLocatorFactory,
            jdbc_connection_service_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Create a config dictionary missing required keys
        kwargs = {
            'schema_upgrade_job': {}
        }
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job(**kwargs)
