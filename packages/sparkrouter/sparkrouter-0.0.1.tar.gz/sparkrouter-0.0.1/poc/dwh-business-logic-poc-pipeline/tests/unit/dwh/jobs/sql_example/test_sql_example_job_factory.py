import unittest

import pytest
from dwh.jobs.sql_example.sql_example_job import SQLExampleJob
from dwh.jobs.sql_example.sql_example_job_factory import SQLExampleJobFactory
from dwh.services.notification.notification_service import NoopNotificationService
from dwh.services.email.email_service import NoopEmailService
from unit.noops import NoopSparkFactory, NoopNotificationServiceFactory, NoopEmailServiceFactory
from utils.mock_sql_execution_service import MockDatabaseConnectionService


class NoopJdbcConnectionServiceFactory:
    """A no-op implementation of JdbcConnectionServiceFactory for testing."""
    
    @staticmethod
    def create_connection(config, spark_session=None):
        """Create a MockDatabaseConnectionService for testing."""
        return MockDatabaseConnectionService()


class TestSQLExampleJobFactory(unittest.TestCase):

    def setUp(self):
        # Use NoopNotificationService and NoopEmailService
        self.notifier = NoopNotificationService()

    def test_sql_example_job_validates_distribution_list_none(self):
        # Test the job validation logic directly without factory
        jdbc_connection_service = MockDatabaseConnectionService()
        email_service = NoopEmailService()

        # Act & Assert
        with pytest.raises(ValueError, match="distribution_list must have at least one entry"):
            SQLExampleJob(
                alarm_service=self.notifier,
                postgres_service=jdbc_connection_service,
                email_service=email_service,
                distribution_list=None,
                from_addr='from@example.com'
            )

    def test_sql_example_job_validates_distribution_list_empty(self):
        # Test the job validation logic directly without factory
        jdbc_connection_service = MockDatabaseConnectionService()
        email_service = NoopEmailService()

        # Act & Assert
        with pytest.raises(ValueError, match="distribution_list must have at least one entry"):
            SQLExampleJob(
                alarm_service=self.notifier,
                postgres_service=jdbc_connection_service,
                email_service=email_service,
                distribution_list=[],
                from_addr='from@example.com'
            )

    def test_sql_example_job_accepts_valid_distribution_list(self):
        # Test that valid parameters work
        jdbc_connection_service = MockDatabaseConnectionService()
        email_service = NoopEmailService()

        # Act
        job = SQLExampleJob(
            alarm_service=self.notifier,
            postgres_service=jdbc_connection_service,
            email_service=email_service,
            distribution_list=['test@example.com'],
            from_addr='from@example.com'
        )

        # Assert
        assert job.distribution_list == ['test@example.com']
        assert job.from_addr == 'from@example.com'

    def test_sql_example_job_parses_string_distribution_list(self):
        # Test that comma-separated string gets parsed
        jdbc_connection_service = MockDatabaseConnectionService()
        email_service = NoopEmailService()

        # Act
        job = SQLExampleJob(
            alarm_service=self.notifier,
            postgres_service=jdbc_connection_service,
            email_service=email_service,
            distribution_list='test1@example.com,test2@example.com',
            from_addr='from@example.com'
        )

        # Assert
        assert job.distribution_list == ['test1@example.com', 'test2@example.com']
        
    def test_factory_creates_job_with_dependencies(self):
        # Arrange
        factory = SQLExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory,
            spark_factory=NoopSparkFactory
        )
        
        # Create a simple config dictionary
        kwargs = {
            'sql_example_job': {
                'alarm_service': {'type': 'noop'},
                'email_service': {'type': 'noop'},
                'postgres_connection': {'type': 'mock'}
            },
            'distribution_list': ['test@example.com'],
            'from_addr': 'from@example.com'
        }
        
        # Act
        job = factory.create_job(**kwargs)
        
        # Assert
        self.assertIsInstance(job, SQLExampleJob)
        self.assertIsInstance(job.alarm_service, NoopNotificationService)
        self.assertIsInstance(job.email_service, NoopEmailService)
        self.assertIsInstance(job.postgres_service, MockDatabaseConnectionService)
        self.assertEqual(job.distribution_list, ['test@example.com'])
        self.assertEqual(job.from_addr, 'from@example.com')

    def test_factory_main_function_exists(self):
        # Test that the main function exists and is callable
        from dwh.jobs.sql_example.sql_example_job_factory import main

        # Assert
        assert callable(main)
        
    def test_factory_raises_error_on_missing_config(self):
        # Arrange
        factory = SQLExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job()
            
    def test_factory_raises_error_on_missing_required_keys(self):
        # Arrange
        factory = SQLExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Create a config dictionary missing required keys
        kwargs = {
            'sql_example_job': {}
        }
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job(**kwargs)
