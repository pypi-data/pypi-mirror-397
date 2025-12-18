import unittest

from dwh.jobs.generic_example.generic_example_job import GenericExampleJob
from dwh.jobs.generic_example.generic_example_job_factory import GenericExampleJobFactory
from dwh.services.notification.notification_service import NoopNotificationService, NotificationService


class NoopNotificationServiceFactory:
    """A no-op implementation of NotificationServiceFactory for testing."""
    
    @staticmethod
    def create_notification_service(config):
        """Create a NoopNotificationService for testing."""
        return NoopNotificationService()


class TestGenericExampleJobFactory(unittest.TestCase):

    def test_generic_example_job_creation(self):
        # Test the job creation logic directly without factory
        notifier = NoopNotificationService()

        # Act
        job = GenericExampleJob(alarm_service=notifier)

        # Assert
        self.assertIs(job.alarm_service, notifier)
        
    def test_factory_creates_job_with_dependencies(self):
        # Arrange
        factory = GenericExampleJobFactory(
            notification_service_factory=NoopNotificationServiceFactory
        )
        
        # Create a simple config dictionary
        kwargs = {
            'generic_example_job': {
                'alarm_service': {
                    'type': 'noop'
                }
            }
        }
        
        # Act
        job = factory.create_job(**kwargs)
        
        # Assert
        self.assertIsInstance(job, GenericExampleJob)
        self.assertIsInstance(job.alarm_service, NotificationService)

    def test_factory_main_function_exists(self):
        # Test that the main function exists and is callable
        from dwh.jobs.generic_example.generic_example_job_factory import main

        # Assert
        self.assertTrue(callable(main))
        
    def test_factory_raises_error_on_missing_config(self):
        # Arrange
        factory = GenericExampleJobFactory(
            notification_service_factory=NoopNotificationServiceFactory
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job()
            
    def test_factory_raises_error_on_missing_alarm_service(self):
        # Arrange
        factory = GenericExampleJobFactory(
            notification_service_factory=NoopNotificationServiceFactory
        )
        
        # Create a config dictionary missing alarm_service
        kwargs = {
            'generic_example_job': {}
        }
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job(**kwargs)
