import unittest

from dwh.jobs.spark_example.spark_example_job import SparkExampleJob
from dwh.jobs.spark_example.spark_example_job_factory import SparkExampleJobFactory
from dwh.services.notification.notification_service import NoopNotificationService
from unit.noops import NoopSparkSession, NoopNotificationServiceFactory, NoopSparkFactory


class TestSparkExampleJobFactory(unittest.TestCase):

    def test_spark_example_job_creation(self):
        # Test the job creation logic directly without factory
        alarm_service = NoopNotificationService()
        success_service = NoopNotificationService()
        spark_session = NoopSparkSession()

        # Act
        job = SparkExampleJob(
            alarm_service=alarm_service,
            success_service=success_service,
            spark_session=spark_session
        )

        # Assert
        self.assertIs(job.alarm_service, alarm_service)
        self.assertIs(job.success_service, success_service)
        self.assertIs(job.spark_session, spark_session)
        
    def test_factory_creates_job_with_dependencies(self):
        # Arrange
        factory = SparkExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            spark_factory=NoopSparkFactory
        )
        
        # Create a simple config dictionary
        kwargs = {
            'spark_example_job': {
                'alarm_service': {'type': 'noop'},
                'success_service': {'type': 'noop'}
            },
            'has_spark': True
        }
        
        # Act
        job = factory.create_job(**kwargs)
        
        # Assert
        self.assertIsInstance(job, SparkExampleJob)
        self.assertIsInstance(job.alarm_service, NoopNotificationService)
        self.assertIsInstance(job.success_service, NoopNotificationService)
        self.assertIsInstance(job.spark_session, NoopSparkSession)

    def test_factory_main_function_exists(self):
        # Test that the main function exists and is callable
        from dwh.jobs.spark_example.spark_example_job_factory import main

        # Assert
        self.assertTrue(callable(main))
        
    def test_factory_raises_error_on_missing_config(self):
        # Arrange
        factory = SparkExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            spark_factory=NoopSparkFactory
        )
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job()
            
    def test_factory_raises_error_on_missing_spark(self):
        # Arrange
        factory = SparkExampleJobFactory(
            notification_factory=NoopNotificationServiceFactory,
            spark_factory=NoopSparkFactory
        )
        
        # Create a config dictionary with has_spark=False
        kwargs = {
            'spark_example_job': {
                'alarm_service': {'type': 'noop'},
                'success_service': {'type': 'noop'}
            },
            'has_spark': False
        }
        
        # Act & Assert
        with self.assertRaises(ValueError):
            factory.create_job(**kwargs)
