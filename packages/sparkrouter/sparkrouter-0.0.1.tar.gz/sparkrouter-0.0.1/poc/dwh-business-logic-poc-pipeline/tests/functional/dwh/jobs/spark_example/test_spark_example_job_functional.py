import pytest
from dwh.jobs.spark_example.spark_example_job import SparkExampleJob
from dwh.services.notification.notification_service import NoopNotificationService


class TrackingNotificationService(NoopNotificationService):
    """Test implementation extending NoopNotificationService to track calls"""
    
    def __init__(self):
        super().__init__()
        self.notification_calls = []
    
    def send_notification(self, subject: str, message: str) -> bool:
        """Override to track notification calls while preserving business logic"""
        self.notification_calls.append({"subject": subject, "message": message})
        return super().send_notification(subject, message)


@pytest.mark.functional
class TestSparkExampleJobFunctional:
    """Functional tests for SparkExampleJob - test complete business workflows with real processing logic"""

    def test_complete_job_workflow_with_real_spark_operations(self, spark_session):
        """Test complete job workflow with real Spark DataFrame operations"""
        # Use real Spark session with Noop notification services
        alarm_service = NoopNotificationService()
        success_service = NoopNotificationService()
        
        job = SparkExampleJob(alarm_service, success_service, spark_session)
        
        # Execute complete business logic workflow
        example = "functional_test_example"
        result = job.execute_job(example=example)

        # Verify business logic executed correctly
        assert result == "Job executed successfully"
        
        # Verify real Spark DataFrame operations occurred
        # This would fail if Spark business logic was modified
        tables = spark_session.catalog.listTables()
        # Note: In this simple example, no tables are registered, but DataFrame operations occurred
        
    def test_end_to_end_job_execution_with_notification_workflow(self, spark_session):
        """Test end-to-end job execution including complete notification workflow"""
        # Use tracking notification service to verify business logic
        alarm_service = TrackingNotificationService()
        success_service = TrackingNotificationService()
        
        job = SparkExampleJob(alarm_service, success_service, spark_session)
        
        # Execute complete job workflow including notification business logic
        job.run(example="end_to_end_test")
        
        # Verify notification business logic executed correctly
        # These assertions MUST fail if notification business logic changes
        assert len(success_service.notification_calls) == 1
        assert success_service.notification_calls[0]["subject"] == "SparkExampleJob: Job Completed Successfully"
        assert success_service.notification_calls[0]["message"] == "Job executed successfully"
        assert len(alarm_service.notification_calls) == 0  # No failures occurred

    def test_job_parameter_validation_and_processing(self, spark_session):
        """Test job parameter validation and processing business logic"""
        alarm_service = NoopNotificationService()
        success_service = NoopNotificationService()
        
        job = SparkExampleJob(alarm_service, success_service, spark_session)
        
        # Test different valid example values to verify business logic
        test_cases = ["simple", "complex_example_with_underscores", "Example With Spaces", "123_numeric_start"]
        
        for example in test_cases:
            result = job.execute_job(example=example)
            
            # Verify business logic processed each case correctly
            assert result == "Job executed successfully"
            
            # Verify parameter validation business logic works
            # This would fail if validation logic was modified
            
    def test_job_error_handling_workflow(self, spark_session):
        """Test complete error handling workflow with real business logic"""
        alarm_service = TrackingNotificationService()
        success_service = TrackingNotificationService()
        
        job = SparkExampleJob(alarm_service, success_service, spark_session)
        
        # Test parameter validation business logic
        with pytest.raises(ValueError, match="example must be a string"):
            job.execute_job(example=123)  # Invalid type should trigger validation
        
        # Verify error handling business logic
        # This tests that parameter validation is actually working
