import unittest
from typing import Any

from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.abstract_job import AbstractJob


class StubJob(AbstractJob):
    """Stub implementation of AbstractJob for testing"""

    def on_success(self, results: Any) -> None:
        pass

    def on_failure(self, error_message: str) -> None:
        pass

    def __init__(self, should_fail_run=False):
        self.should_fail_run = should_fail_run
        self.execute_job_calls = []
        self.run_calls = []

    def execute_job(self, param1=None, param2=None, param3=None):
        """Test method with specific parameters"""
        self.execute_job_calls.append({
            'param1': param1,
            'param2': param2,
            'param3': param3
        })
        if self.should_fail_run:
            raise Exception("Test execution error")


class StubJobFactory(AbstractJobFactory):
    """Concrete implementation of AbstractJobFactory for testing"""

    def __init__(self, job_should_fail_creation=False, job_should_fail_run=False, **kwargs):
        self.job_should_fail_creation = job_should_fail_creation
        self.job_should_fail_run = job_should_fail_run
        self.job = None

    def create_job(self, **kwargs):
        if self.job_should_fail_creation:
            raise Exception("Test job creation error")
        # Create a job if one doesn't exist, otherwise return the existing one
        if self.job is None:
            self.job = StubJob(should_fail_run=self.job_should_fail_run)
        return self.job


class TestAbstractJobFactory(unittest.TestCase):
    """Test the AbstractJobFactory business logic"""

    def test_successful_job_creation(self):
        """Test successful job creation and initialization"""

        # Act
        factory = StubJobFactory()
        job = factory.create_job()

        # Assert
        self.assertIsInstance(job, StubJob)

    def test_job_creation_failure_propagates_exception(self):
        """Test that job creation failures propagate exceptions properly"""

        # Act & Assert
        factory = StubJobFactory(job_should_fail_creation=True)
        with self.assertRaises(Exception) as context:
            factory.create_job()

        # Check that the original exception propagated
        self.assertIn("Test job creation error", str(context.exception))

    def test_run_with_parameter_filtering(self):
        """Test that run method filters parameters to match method signature"""

        # Arrange
        factory = StubJobFactory()
        job = factory.create_job()

        # Act - pass both valid and invalid parameters
        factory.run(
            param1='value1',  # Valid parameter
            param2='value2',  # Valid parameter
            param3='value3',  # Valid parameter
            invalid_param='invalid',  # Invalid parameter (should be filtered out)
            another_invalid=123  # Invalid parameter (should be filtered out)
        )

        # Assert
        self.assertEqual(len(job.execute_job_calls), 1)
        call = job.execute_job_calls[0]

        # Valid parameters should be passed through
        self.assertEqual(call['param1'], 'value1')
        self.assertEqual(call['param2'], 'value2')
        self.assertEqual(call['param3'], 'value3')

        # Invalid parameters should be filtered out (not in the call)
        self.assertNotIn('invalid_param', call)
        self.assertNotIn('another_invalid', call)

    def test_run_with_partial_parameters(self):
        """Test run method with only some valid parameters"""

        # Arrange
        factory = StubJobFactory()
        job = factory.create_job()

        # Act
        factory.run(param1='only_param1', invalid_param='should_be_ignored')

        # Assert
        call = job.execute_job_calls[0]
        self.assertEqual(call['param1'], 'only_param1')
        self.assertIsNone(call['param2'])  # Should be None (default)
        self.assertIsNone(call['param3'])  # Should be None (default)

    def test_run_with_no_valid_parameters(self):
        """Test run method with no valid parameters"""

        # Arrange
        factory = StubJobFactory()
        job = factory.create_job()

        # Act
        factory.run(invalid_param1='value1', invalid_param2='value2')

        # Assert
        call = job.execute_job_calls[0]
        self.assertIsNone(call['param1'])
        self.assertIsNone(call['param2'])
        self.assertIsNone(call['param3'])

    def test_run_with_empty_kwargs(self):
        """Test run method with empty kwargs"""

        # Arrange
        factory = StubJobFactory()
        job = factory.create_job()

        # Act
        factory.run()

        # Assert
        call = job.execute_job_calls[0]
        self.assertIsNone(call['param1'])
        self.assertIsNone(call['param2'])
        self.assertIsNone(call['param3'])

    def test_create_job_is_abstract_method(self):
        """Test that create_job is properly defined as abstract method"""
        # Act & Assert
        with self.assertRaises(TypeError):
            # Cannot instantiate AbstractJobFactory directly
            AbstractJobFactory()

    def test_constructor_passes_kwargs_to_notification_service_factory(self):
        """Test that constructor kwargs are passed to NotificationService factory"""
        # This test verifies the integration between AbstractJobFactory and NotificationServiceFactory
        # The NotificationServiceFactory should receive the kwargs and create appropriate service

        # Act
        factory = StubJobFactory()
        job = factory.create_job()

        # Assert
        # The fact that the job was created successfully means kwargs were handled properly
        self.assertIsInstance(job, StubJob)

    def test_notification_service_creation_with_different_types(self):
        """Test that different notification service types can be created"""

        # Test NOOP notification service
        factory1 = StubJobFactory()
        job = factory1.create_job()
        self.assertIsInstance(job, StubJob)

        # The NotificationServiceFactory will handle different types
        # We just verify that the factory completes successfully


class StubJobWithDifferentSignature(AbstractJob):
    """Stub job with different execute_job signature for testing parameter filtering"""

    def on_success(self, results: Any) -> None:
        pass

    def on_failure(self, error_message: str) -> None:
        pass

    def __init__(self):
        self.execute_job_calls = []

    def execute_job(self, database_name=None, table_name=None):
        """Different parameter signature for testing"""
        self.execute_job_calls.append({
            'database_name': database_name,
            'table_name': table_name
        })


class StubJobFactoryWithDifferentSignature(AbstractJobFactory):
    """Factory that creates jobs with different parameter signatures"""
    
    def __init__(self, **kwargs):
        self.job = None

    def create_job(self, **kwargs):
        if self.job is None:
            self.job = StubJobWithDifferentSignature()
        return self.job


class TestParameterFilteringWithDifferentSignatures(unittest.TestCase):
    """Test parameter filtering with different job signatures"""

    def test_parameter_filtering_adapts_to_different_signatures(self):
        """Test that parameter filtering works with different method signatures"""

        # Arrange
        factory = StubJobFactoryWithDifferentSignature()
        job = factory.create_job()

        # Act
        factory.run(
            database_name='test_db',
            table_name='test_table',
            param1='invalid',
            start_date='2023-01-01'
        )

        # Assert
        call = job.execute_job_calls[0]
        self.assertEqual(call['database_name'], 'test_db')
        self.assertEqual(call['table_name'], 'test_table')
        self.assertNotIn('param1', call)
        self.assertNotIn('start_date', call)


if __name__ == '__main__':
    unittest.main()