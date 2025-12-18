import unittest

from dwh.jobs.sql_example.sql_example_job import SQLExampleJob
from dwh.services.notification.notification_service import NoopNotificationService, NotificationService
from dwh.services.email.email_service import NoopEmailService, EmailService
from utils.mock_sql_execution_service import MockDatabaseConnectionService


class StubSQLExampleJob(SQLExampleJob):
    """Test subclass that accepts SQL directly instead of reading from file"""

    def __init__(self, sql_content="SELECT * FROM test_table WHERE date BETWEEN :start_dt AND :end_dt", **kwargs):
        # Set the SQL content directly instead of reading from file
        self.sql = sql_content

        # Initialize parent without calling super().__init__ to avoid file reading
        if not isinstance(kwargs['email_service'], EmailService):
            raise ValueError("email_service must be an instance of EmailService")
        if not isinstance(kwargs['alarm_service'], NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        distribution_list = kwargs['distribution_list']
        if isinstance(distribution_list, str):
            distribution_list = distribution_list.split(',')
        elif not distribution_list or not isinstance(distribution_list, list):
            raise ValueError("distribution_list must have at least one entry")

        for email in distribution_list:
            if not self.EMAIL_REGEX.fullmatch(email):
                raise ValueError(f"Invalid email address in distribution_list: {email}")

        if not self.EMAIL_REGEX.fullmatch(kwargs['from_addr']):
            raise ValueError("from_addr must be a valid email address")

        self.distribution_list = distribution_list
        self.from_addr = kwargs['from_addr']
        self.alarm_service = kwargs['alarm_service']
        self.email_service = kwargs['email_service']
        self.postgres_service = kwargs['postgres_service']


class TestSQLExampleJobTests(unittest.TestCase):

    def setUp(self):
        # Use NoopNotificationService and NoopEmailService
        self.alarm_service = NoopNotificationService()
        self.email_service = NoopEmailService()
        self.postgres_service = MockDatabaseConnectionService()

        # Valid email addresses
        self.from_addr = "test@example.com"
        self.distribution_list = ["user1@example.com", "user2@example.com"]

        # Create the test job with SQL content directly
        self.job = StubSQLExampleJob(
            sql_content="SELECT * FROM test_table WHERE date BETWEEN :start_dt AND :end_dt",
            alarm_service=self.alarm_service,
            postgres_service=self.postgres_service,
            email_service=self.email_service,
            distribution_list=self.distribution_list,
            from_addr=self.from_addr
        )

    def test_init_with_valid_parameters(self):
        # Test initialization with valid parameters
        job = StubSQLExampleJob(
            alarm_service=self.alarm_service,
            postgres_service=self.postgres_service,
            email_service=self.email_service,
            distribution_list=self.distribution_list,
            from_addr=self.from_addr
        )

        self.assertEqual(job.distribution_list, self.distribution_list)
        self.assertEqual(job.from_addr, self.from_addr)
        self.assertEqual(job.alarm_service, self.alarm_service)
        self.assertEqual(job.postgres_service, self.postgres_service)
        self.assertEqual(job.email_service, self.email_service)

    def test_init_with_string_distribution_list(self):
        # Test initialization with distribution list as a comma-separated string
        job = StubSQLExampleJob(
            alarm_service=self.alarm_service,
            postgres_service=self.postgres_service,
            email_service=self.email_service,
            distribution_list="user1@example.com,user2@example.com",
            from_addr=self.from_addr
        )

        self.assertEqual(job.distribution_list, ["user1@example.com", "user2@example.com"])

    def test_init_with_invalid_email_service(self):
        # Test initialization with invalid email service
        with self.assertRaises(ValueError) as context:
            StubSQLExampleJob(
                alarm_service=self.alarm_service,
                postgres_service=self.postgres_service,
                email_service="not_an_email_service",
                distribution_list=self.distribution_list,
                from_addr=self.from_addr
            )

        self.assertEqual(str(context.exception), "email_service must be an instance of EmailService")

    def test_init_with_invalid_notification_service(self):
        # Test initialization with invalid notification service
        with self.assertRaises(ValueError) as context:
            StubSQLExampleJob(
                alarm_service="not_a_notification_service",
                postgres_service=self.postgres_service,
                email_service=self.email_service,
                distribution_list=self.distribution_list,
                from_addr=self.from_addr
            )

        self.assertEqual(str(context.exception), "alarm_service must be an instance of NotificationService")

    def test_init_with_invalid_distribution_list(self):
        # Test initialization with invalid distribution list
        with self.assertRaises(ValueError) as context:
            StubSQLExampleJob(
                alarm_service=self.alarm_service,
                postgres_service=self.postgres_service,
                email_service=self.email_service,
                distribution_list=[],
                from_addr=self.from_addr
            )

        self.assertEqual(str(context.exception), "distribution_list must have at least one entry")

    def test_init_with_invalid_email_in_distribution_list(self):
        # Test initialization with invalid email in distribution list
        with self.assertRaises(ValueError) as context:
            StubSQLExampleJob(
                alarm_service=self.alarm_service,
                postgres_service=self.postgres_service,
                email_service=self.email_service,
                distribution_list=["not_an_email", "user@example.com"],
                from_addr=self.from_addr
            )

        self.assertEqual(str(context.exception), "Invalid email address in distribution_list: not_an_email")

    def test_init_with_invalid_from_addr(self):
        # Test initialization with invalid from_addr
        with self.assertRaises(ValueError) as context:
            StubSQLExampleJob(
                alarm_service=self.alarm_service,
                postgres_service=self.postgres_service,
                email_service=self.email_service,
                distribution_list=self.distribution_list,
                from_addr="not_an_email"
            )

        self.assertEqual(str(context.exception), "from_addr must be a valid email address")

    def test_validate_params_valid_dates(self):
        # Test with valid dates
        start_date = "2023-01-01"
        end_date = "2023-01-31"

        # Should not raise any exceptions
        self.job.validate_params(start_date, end_date)

    def test_validate_params_missing_start_date(self):
        # Test with missing start date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params(None, "2023-01-31")

        self.assertEqual(str(context.exception), "start_date is required")

    def test_validate_params_missing_end_date(self):
        # Test with missing end date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params("2023-01-01", None)

        self.assertEqual(str(context.exception), "end_date is required")

    def test_validate_params_invalid_start_date_format(self):
        # Test with invalid start date format
        with self.assertRaises(ValueError) as context:
            self.job.validate_params("01/01/2023", "2023-01-31")

        self.assertEqual(str(context.exception), "start_date must be formatted as 'YYYY-MM-DD'")

    def test_validate_params_invalid_end_date_format(self):
        # Test with invalid end date format
        with self.assertRaises(ValueError) as context:
            self.job.validate_params("2023-01-01", "31/01/2023")

        self.assertEqual(str(context.exception), "end_date must be formatted as 'YYYY-MM-DD'")

    def test_validate_params_end_before_start(self):
        # Test with end date before start date
        with self.assertRaises(ValueError) as context:
            self.job.validate_params("2023-01-31", "2023-01-01")

        self.assertEqual(str(context.exception), "end_date cannot be before start_date")

    def test_execute_query(self):
        # Test execute_query method
        results = self.job.execute_query("2023-01-01", "2023-01-31")

        # Verify results
        self.assertEqual(results, [{'column1': 'value1', 'column2': 'value2'}])

        # Verify that postgres_service.execute_query was called with the right parameters
        self.assertEqual(len(self.postgres_service.executed_queries), 1)
        self.assertEqual(len(self.postgres_service.executed_params), 1)
        self.assertEqual(self.postgres_service.executed_params[0], {
            'start_dt': '2023-01-01',
            'end_dt': '2023-01-31'
        })

    def test_execute_job(self):
        # Track email sending
        original_send_email = self.email_service.send_email
        email_sent = False

        def track_email_send(msg, from_addr, bcc_addr):
            nonlocal email_sent
            email_sent = True
            self.assertEqual(from_addr, self.from_addr)
            self.assertEqual(bcc_addr, self.distribution_list)
            self.assertIn('Glue Job Success Email: 2023-01-01', msg['Subject'])
            return True

        try:
            self.email_service.send_email = track_email_send

            # Execute the job
            results = self.job.execute_job("2023-01-01", "2023-01-31")

            # Verify results
            self.assertEqual(results, [{'column1': 'value1', 'column2': 'value2'}])

            # Verify email was sent
            self.assertTrue(email_sent)

            # Verify that postgres_service.execute_query was called with the right parameters
            self.assertEqual(len(self.postgres_service.executed_queries), 1)
            self.assertEqual(len(self.postgres_service.executed_params), 1)
            self.assertEqual(self.postgres_service.executed_params[0], {
                'start_dt': '2023-01-01',
                'end_dt': '2023-01-31'
            })

        finally:
            # Restore original method
            self.email_service.send_email = original_send_email


if __name__ == "__main__":
    unittest.main()
