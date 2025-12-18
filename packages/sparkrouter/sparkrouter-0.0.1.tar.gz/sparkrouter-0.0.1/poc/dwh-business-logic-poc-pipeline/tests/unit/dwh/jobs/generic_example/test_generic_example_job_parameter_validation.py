"""
Unit tests for GenericExampleJob parameter validation
"""
import pytest
from dwh.jobs.generic_example.generic_example_job_factory import GenericExampleJobFactory
from unit.noops import NoopNotificationServiceFactory


class TestGenericExampleJobParameterValidation:
    """Unit tests for parameter validation in GenericExampleJob"""

    @pytest.fixture
    def job_factory(self):
        """Create job factory with Noop dependencies"""
        return GenericExampleJobFactory(
            notification_service_factory=NoopNotificationServiceFactory()
        )

    @pytest.fixture
    def valid_config(self):
        """Valid job configuration for testing"""
        return {
            "generic_example_job": {
                "alarm_service": {
                    "notification_service": "NOOP"
                }
            }
        }

    def test_valid_parameters(self, job_factory, valid_config):
        """Test job creation and execution with valid parameters"""
        job = job_factory.create_job(**valid_config)
        assert job is not None
        
        # Test that execute_job works with valid dates
        result = job.execute_job(start_date="2023-01-01", end_date="2023-01-31")
        assert "Job executed successfully" in result

    def test_end_date_before_start_date_fails(self, job_factory, valid_config):
        """Test that end_date before start_date raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(ValueError, match="end_date cannot be before start_date"):
            job.execute_job(start_date="2023-01-31", end_date="2023-01-01")

    def test_invalid_date_format_start_date(self, job_factory, valid_config):
        """Test that invalid start_date format raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(ValueError, match="start_date must be formatted as 'YYYY-MM-DD'"):
            job.execute_job(start_date="invalid-date", end_date="2023-01-31")

    def test_invalid_date_format_end_date(self, job_factory, valid_config):
        """Test that invalid end_date format raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(ValueError, match="end_date must be formatted as 'YYYY-MM-DD'"):
            job.execute_job(start_date="2023-01-01", end_date="not-a-date")

    def test_missing_required_config(self, job_factory):
        """Test that missing generic_example_job config raises ValueError"""
        with pytest.raises(ValueError, match="generic_example_job value must be a dict"):
            job_factory.create_job()

    def test_empty_config_fails(self, job_factory):
        """Test that empty config raises ValueError"""
        invalid_config = {
            "generic_example_job": {}
        }
        
        with pytest.raises(ValueError, match="Configuration for 'generic_example_job' is required"):
            job_factory.create_job(**invalid_config)
    
    def test_missing_alarm_service_config(self, job_factory):
        """Test that missing alarm_service config raises ValueError"""
        invalid_config = {
            "generic_example_job": {
                "some_other_key": "value"
            }
        }
        
        with pytest.raises(ValueError, match="Missing required configuration key.*alarm_service"):
            job_factory.create_job(**invalid_config)

    def test_invalid_notification_service_type_with_real_factory(self, valid_config):
        """Test that invalid notification service type raises ValueError with real factory"""
        from dwh.services.notification.notification_service_factory import NotificationServiceFactory
        
        # Use real factory to test actual validation
        real_factory = GenericExampleJobFactory(
            notification_service_factory=NotificationServiceFactory
        )
        
        invalid_config = {
            "generic_example_job": {
                "alarm_service": {
                    "notification_service": "INVALID_SERVICE"
                }
            }
        }
        
        with pytest.raises(ValueError, match="Unsupported notification_service.*INVALID_SERVICE"):
            real_factory.create_job(**invalid_config)

    def test_missing_start_date_parameter(self, job_factory, valid_config):
        """Test that missing start_date parameter raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(TypeError, match="missing.*required.*argument.*start_date"):
            job.execute_job(end_date="2023-01-31")

    def test_missing_end_date_parameter(self, job_factory, valid_config):
        """Test that missing end_date parameter raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(TypeError, match="missing.*required.*argument.*end_date"):
            job.execute_job(start_date="2023-01-01")

    def test_empty_start_date_parameter(self, job_factory, valid_config):
        """Test that empty start_date parameter raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(ValueError, match="start_date is required"):
            job.execute_job(start_date="", end_date="2023-01-31")

    def test_empty_end_date_parameter(self, job_factory, valid_config):
        """Test that empty end_date parameter raises ValueError"""
        job = job_factory.create_job(**valid_config)
        
        with pytest.raises(ValueError, match="end_date is required"):
            job.execute_job(start_date="2023-01-01", end_date="")