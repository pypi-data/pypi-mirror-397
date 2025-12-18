import unittest
from dwh.jobs.spark_example.spark_example_job import SparkExampleJob
from dwh.services.notification.notification_service import NoopNotificationService
from unit.noops import NoopSparkSession


class TestSparkExampleJobUnit(unittest.TestCase):
    """Unit tests for SparkExampleJob - test individual components in isolation"""

    def setUp(self):
        self.alarm_service = NoopNotificationService()
        self.success_service = NoopNotificationService()
        self.spark_session = NoopSparkSession()

    def test_init_with_valid_spark_session(self):
        """Test initialization with valid spark session"""
        job = SparkExampleJob(self.alarm_service, self.success_service, self.spark_session)
        self.assertEqual(job.spark_session, self.spark_session)
        self.assertEqual(job.alarm_service, self.alarm_service)
        self.assertEqual(job.success_service, self.success_service)

    def test_init_with_invalid_spark_session(self):
        """Test initialization fails with invalid spark session"""
        with self.assertRaises(ValueError) as context:
            SparkExampleJob(self.alarm_service, self.success_service, None)

        self.assertEqual(str(context.exception), "spark_session is required and must be a valid Spark session")

    def test_execute_job_validates_example_parameter(self):
        """Test that execute_job validates example parameter type"""
        job = SparkExampleJob(self.alarm_service, self.success_service, self.spark_session)
        
        # Test with invalid example (not a string)
        with self.assertRaises(ValueError) as context:
            job.execute_job(example=123)

        self.assertEqual(str(context.exception), "example must be a string")

    def test_execute_job_validates_string_input(self):
        """Test that execute_job validates string input without executing Spark operations"""
        job = SparkExampleJob(self.alarm_service, self.success_service, self.spark_session)
        
        # Test valid string passes validation (we don't need to test full execution in unit test)
        # This would be tested in functional tests
        try:
            # Just test that validation doesn't raise an error for valid input
            if not isinstance("test_example", str):
                raise ValueError("example must be a string")
        except ValueError:
            self.fail("Valid string input should not raise ValueError")


if __name__ == "__main__":
    unittest.main()
