import pytest

from dwh.jobs.revenue_recon.revenue_recon_job import RevenueReconJob
from dwh.jobs.revenue_recon.revenue_recon_job_factory import RevenueReconJobFactory
from dwh.services.notification.notification_service import NoopNotificationService
from dwh.services.email.email_service import NoopEmailService
from utils.mock_sql_execution_service import MockDatabaseConnectionService


class NoopNotificationServiceFactory:
    """A no-op implementation of NotificationServiceFactory for testing."""
    
    @staticmethod
    def create_notification_service(config):
        """Create a NoopNotificationService for testing."""
        return NoopNotificationService()


class NoopEmailServiceFactory:
    """A no-op implementation of EmailServiceFactory for testing."""
    
    @staticmethod
    def create_email_service(config):
        """Create a NoopEmailService for testing."""
        return NoopEmailService()


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


class TestRevenueReconJobFactory:

    def test_revenue_recon_job_creation(self):
        # Test the job creation logic directly without factory
        notifier = NoopNotificationService()
        success = NoopNotificationService()
        jdbc_connection_service = MockDatabaseConnectionService()
        email_service = NoopEmailService()

        # Act
        job = RevenueReconJob(
            alarm_service=notifier,
            success_service=success,
            postgres_service=jdbc_connection_service,
            email_service=email_service,
            distribution_list=['test@example.com'],
            from_addr='noreply@example.com'
        )

        # Assert
        assert job.alarm_service is notifier
        assert job.postgres_service is jdbc_connection_service
        assert job.email_service is email_service
        assert job.distribution_list == ['test@example.com']
        assert job.from_addr == 'noreply@example.com'
        
    def test_factory_creates_job_with_dependencies(self):
        # Arrange
        factory = RevenueReconJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory,
            spark_factory=NoopSparkSessionFactory
        )
        
        # Create a simple config dictionary
        kwargs = {
            'revenue_recon_job': {
                'alarm_service': {'type': 'noop'},
                'success_service': {'type': 'noop'},
                'email_service': {'type': 'noop'},
                'postgres_connection': {'type': 'mock'}
            },
            'distribution_list': ['test@example.com'],
            'from_addr': 'noreply@example.com'
        }
        
        # Act
        job = factory.create_job(**kwargs)
        
        # Assert
        assert isinstance(job, RevenueReconJob)
        assert isinstance(job.alarm_service, NoopNotificationService)
        assert isinstance(job.success_service, NoopNotificationService)
        assert isinstance(job.email_service, NoopEmailService)
        assert isinstance(job.postgres_service, MockDatabaseConnectionService)
        assert job.distribution_list == ['test@example.com']
        assert job.from_addr == 'noreply@example.com'

    def test_factory_main_function_exists(self):
        # Test that the main function exists and is callable
        from dwh.jobs.revenue_recon.revenue_recon_job_factory import main

        # Assert
        assert callable(main)
        
    def test_factory_raises_error_on_missing_config(self):
        # Arrange
        factory = RevenueReconJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Act & Assert
        with pytest.raises(ValueError):
            factory.create_job()
            
    def test_factory_raises_error_on_missing_required_keys(self):
        # Arrange
        factory = RevenueReconJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            email_factory=NoopEmailServiceFactory,
            jdbc_factory=NoopJdbcConnectionServiceFactory
        )
        
        # Create a config dictionary missing required keys
        kwargs = {
            'revenue_recon_job': {}
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Missing required configuration key: 'alarm_service'"):
            factory.create_job(**kwargs)
