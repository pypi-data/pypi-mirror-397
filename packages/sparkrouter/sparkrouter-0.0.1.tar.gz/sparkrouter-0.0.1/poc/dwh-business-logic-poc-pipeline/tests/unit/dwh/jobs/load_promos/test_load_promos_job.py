import unittest
from dwh.jobs.load_promos.load_promos_job import LoadPromosJob
from dwh.services.notification.notification_service import NoopNotificationService


class NoopDataFrame:
    """Noop DataFrame for unit testing"""

    def __init__(self, count=2):
        self._count = count
        self.columns = ["_id", "updatedate", "ptn_ingress_date", "promotionid"]

    def count(self):
        return self._count

    def filter(self, condition):
        return NoopDataFrame(0)  # No null values

    def select(self, *cols):
        return self

    def distinct(self):
        return self


class NoopExtractor:
    def __init__(self):
        self.extract_called = False

    def extract(self, start_date, end_date):
        self.extract_called = True
        return NoopDataFrame()


class NoopValidator:
    def __init__(self):
        self.validate_called = False

    def validate(self, df):
        self.validate_called = True


class NoopTransformer:
    def __init__(self):
        self.transform_called = False

    def transform(self, df, created_by):
        self.transform_called = True
        return NoopDataFrame()


class NoopLoader:
    def __init__(self):
        self.load_called = False

    def load(self, df=None):
        self.load_called = True


class NoopLoadValidator:
    def __init__(self):
        self.validate_called = False

    def validate(self, start_date, end_date):
        self.validate_called = True

class TestLoadPromosJob(unittest.TestCase):
    def setUp(self):
        self.alarm_service = NoopNotificationService()
        self.success_service = NoopNotificationService()

        # Create noop components
        self.promotion_extractor = NoopExtractor()
        self.extract_dq_validator = NoopValidator()
        self.promotion_transformer = NoopTransformer()
        self.transform_dq_validator = NoopValidator()
        self.unity_loader = NoopLoader()
        self.unity_dq_validator = NoopLoadValidator()
        self.stage_loader = NoopLoader()
        self.stage_dq_validator = NoopLoadValidator()
        self.redshift_loader = NoopLoader()
        self.redshift_dq_validator = NoopLoadValidator()

        self.job = LoadPromosJob(
            alarm_service=self.alarm_service,
            success_service=self.success_service,
            promotion_extractor=self.promotion_extractor,
            extract_dq_validator=self.extract_dq_validator,
            promotion_transformer=self.promotion_transformer,
            transform_dq_validator=self.transform_dq_validator,
            unity_loader=self.unity_loader,
            unity_dq_validator=self.unity_dq_validator,
            stage_loader=self.stage_loader,
            stage_dq_validator=self.stage_dq_validator,
            redshift_loader=self.redshift_loader,
            redshift_dq_validator=self.redshift_dq_validator
        )

    def test_initialization(self):
        """Test that the job initializes correctly."""
        self.assertIsInstance(self.job.alarm_service, NoopNotificationService)
        self.assertIsInstance(self.job.success_service, NoopNotificationService)
        self.assertEqual(self.job.promotion_extractor, self.promotion_extractor)
        self.assertEqual(self.job.extract_dq_validator, self.extract_dq_validator)
        self.assertEqual(self.job.promotion_transformer, self.promotion_transformer)
        self.assertEqual(self.job.transform_dq_validator, self.transform_dq_validator)
        self.assertEqual(self.job.unity_loader, self.unity_loader)
        self.assertEqual(self.job.unity_dq_validator, self.unity_dq_validator)
        self.assertEqual(self.job.stage_loader, self.stage_loader)
        self.assertEqual(self.job.stage_dq_validator, self.stage_dq_validator)
        self.assertEqual(self.job.redshift_loader, self.redshift_loader)
        self.assertEqual(self.job.redshift_dq_validator, self.redshift_dq_validator)

    def test_initialization_invalid_services(self):
        """Test that initialization fails with invalid service types."""
        with self.assertRaises(ValueError):
            LoadPromosJob(
                alarm_service="not a notification service",
                success_service=self.success_service,
                promotion_extractor=self.promotion_extractor,
                extract_dq_validator=self.extract_dq_validator,
                promotion_transformer=self.promotion_transformer,
                transform_dq_validator=self.transform_dq_validator,
                unity_loader=self.unity_loader,
                unity_dq_validator=self.unity_dq_validator,
                stage_loader=self.stage_loader,
                stage_dq_validator=self.stage_dq_validator,
                redshift_loader=self.redshift_loader,
                redshift_dq_validator=self.redshift_dq_validator
            )

        with self.assertRaises(ValueError):
            LoadPromosJob(
                alarm_service=self.alarm_service,
                success_service="not a notification service",
                promotion_extractor=self.promotion_extractor,
                extract_dq_validator=self.extract_dq_validator,
                promotion_transformer=self.promotion_transformer,
                transform_dq_validator=self.transform_dq_validator,
                unity_loader=self.unity_loader,
                unity_dq_validator=self.unity_dq_validator,
                stage_loader=self.stage_loader,
                stage_dq_validator=self.stage_dq_validator,
                redshift_loader=self.redshift_loader,
                redshift_dq_validator=self.redshift_dq_validator
            )

    def test_execute_job_pipeline(self):
        """Test that execute_job calls all pipeline components in correct order."""
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        created_by = "test_user"

        # Execute the job
        self.job.execute_job(
            start_date=start_date,
            end_date=end_date,
            created_by=created_by
        )

        # Verify all components were called
        self.assertTrue(self.promotion_extractor.extract_called, "Extractor was not called")
        self.assertTrue(self.extract_dq_validator.validate_called, "Extract DQ validator was not called")
        self.assertTrue(self.promotion_transformer.transform_called, "Transformer was not called")
        self.assertTrue(self.transform_dq_validator.validate_called, "Transform DQ validator was not called")
        self.assertTrue(self.unity_loader.load_called, "Unity loader was not called")
        self.assertTrue(self.unity_dq_validator.validate_called, "Unity DQ validator was not called")
        self.assertTrue(self.stage_loader.load_called, "Stage loader was not called")
        self.assertTrue(self.stage_dq_validator.validate_called, "Stage DQ validator was not called")
        self.assertTrue(self.redshift_loader.load_called, "Redshift loader was not called")
        self.assertTrue(self.redshift_dq_validator.validate_called, "Redshift DQ validator was not called")

    def test_execute_job_invalid_date_format(self):
        """Test that execute_job raises ValueError when dates are in invalid format."""
        start_date = "01/01/2023"  # Not ISO format
        end_date = "31/01/2023"  # Not ISO format
        created_by = "test_user"

        with self.assertRaises(ValueError):
            self.job.execute_job(
                start_date=start_date,
                end_date=end_date,
                created_by=created_by
            )

    def test_execute_job_missing_created_by(self):
        """Test that execute_job raises ValueError when created_by is missing."""
        start_date = "2023-01-01"
        end_date = "2023-01-31"

        with self.assertRaises(ValueError):
            self.job.execute_job(
                start_date=start_date,
                end_date=end_date,
                created_by=""
            )

    def test_on_success(self):
        """Test that on_success calls send_notification on the success service."""

        class TrackingNotificationService(NoopNotificationService):
            def __init__(self):
                self.was_called = False
                self.subject = ""
                self.message = ""

            def send_notification(self, subject, message):
                self.was_called = True
                self.subject = subject
                self.message = message
                return True

        tracking_service = TrackingNotificationService()
        original_service = self.job.success_service
        self.job.success_service = tracking_service

        try:
            self.job.on_success("Test results")

            self.assertTrue(tracking_service.was_called)
            self.assertIn("Job", tracking_service.subject)
            self.assertEqual("Test results", tracking_service.message)
        finally:
            self.job.success_service = original_service

    def test_on_failure(self):
        """Test that on_failure calls send_notification on the alarm service."""

        class TrackingNotificationService(NoopNotificationService):
            def __init__(self):
                self.was_called = False
                self.subject = ""
                self.message = ""

            def send_notification(self, subject, message):
                self.was_called = True
                self.subject = subject
                self.message = message
                return True

        tracking_service = TrackingNotificationService()
        original_service = self.job.alarm_service
        self.job.alarm_service = tracking_service

        try:
            self.job.on_failure("Test error")

            self.assertTrue(tracking_service.was_called)
            self.assertIn("Job", tracking_service.subject)
            self.assertEqual("Test error", tracking_service.message)
        finally:
            self.job.alarm_service = original_service


if __name__ == '__main__':
    unittest.main()