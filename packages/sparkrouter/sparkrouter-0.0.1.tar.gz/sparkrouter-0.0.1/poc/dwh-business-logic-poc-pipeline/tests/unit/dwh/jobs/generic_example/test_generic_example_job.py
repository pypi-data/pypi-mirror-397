import unittest
from dwh.jobs.generic_example.generic_example_job import GenericExampleJob
from dwh.services.notification.notification_service import NoopNotificationService


class TestGenericExampleJob(unittest.TestCase):

    def setUp(self):
        self.notifier = NoopNotificationService()
        self.job = GenericExampleJob(self.notifier)

    def test_execute_job_valid_dates(self):
        # Test with valid dates
        start_date = "2023-01-01"
        end_date = "2023-01-31"

        # Execute the job
        self.job.run(start_date=start_date, end_date=end_date)

        # No assertions needed as the method should complete without errors

    def test_validate_params_missing_start_date(self):
        # Test with missing start date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(start_date=None, end_date="2023-01-31")

        self.assertEqual(str(context.exception), "start_date is required")

    def test_validate_params_missing_end_date(self):
        # Test with missing end date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(start_date="2023-01-01", end_date=None)

        self.assertEqual(str(context.exception), "end_date is required")

    def test_validate_params_invalid_start_date_format(self):
        # Test with invalid start date format
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(start_date="01/01/2023", end_date="2023-01-31")

        self.assertEqual(str(context.exception), "start_date must be formatted as 'YYYY-MM-DD'")

    def test_validate_params_invalid_end_date_format(self):
        # Test with invalid end date format
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(start_date="2023-01-01", end_date="31/01/2023")

        self.assertEqual(str(context.exception), "end_date must be formatted as 'YYYY-MM-DD'")

    def test_validate_params_end_before_start(self):
        # Test with end date before start date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(start_date="2023-01-31", end_date="2023-01-01")

        self.assertEqual(str(context.exception), "end_date cannot be before start_date")

    def test_run_success(self):
        # Test successful run
        original_execute_job = self.job.execute_job
        executed = False

        def mock_execute_job(start_date, end_date):
            nonlocal executed
            executed = True
            self.assertEqual(start_date, "2023-01-01")
            self.assertEqual(end_date, "2023-01-31")

        try:
            self.job.execute_job = mock_execute_job
            self.job.run(start_date="2023-01-01", end_date="2023-01-31")
            self.assertTrue(executed, "execute_job was not called")
        finally:
            # Restore original method
            self.job.execute_job = original_execute_job

    def test_run_failure(self):
        # Test run with failure
        error_msg = "Test error"
        original_execute_job = self.job.execute_job
        original_send_notification = self.notifier.send_notification

        notification_sent = False
        notification_subject = ""
        notification_message = ""

        def mock_execute_job(start_date, end_date):
            raise ValueError(error_msg)

        def mock_send_notification(subject, message):
            nonlocal notification_sent, notification_subject, notification_message
            notification_sent = True
            notification_subject = subject
            notification_message = message
            return True

        try:
            self.job.execute_job = mock_execute_job
            self.notifier.send_notification = mock_send_notification

            # Run should raise RuntimeError
            with self.assertRaises(RuntimeError):
                self.job.run(start_date="2023-01-01", end_date="2023-01-31")

            # Verify notification was sent
            self.assertTrue(notification_sent, "Notification was not sent")
            # Check that the subject and message contain the error
            self.assertIn("Failed", notification_subject)
            self.assertIn(error_msg, notification_message)
        finally:
            # Restore original methods
            self.job.execute_job = original_execute_job
            self.notifier.send_notification = original_send_notification


if __name__ == "__main__":
    unittest.main()
