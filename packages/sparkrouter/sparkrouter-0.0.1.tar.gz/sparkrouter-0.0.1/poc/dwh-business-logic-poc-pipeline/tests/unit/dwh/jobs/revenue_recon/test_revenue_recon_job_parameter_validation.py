"""
Unit tests for RevenueReconJob parameter validation
"""
import pytest
from dwh.jobs.revenue_recon.revenue_recon_job_factory import RevenueReconJobFactory
from unit.noops import NoopNotificationServiceFactory, NoopEmailServiceFactory, NoopJdbcConnectionServiceFactory


class TestRevenueReconJobParameterValidation:
    """Unit tests for parameter validation in RevenueReconJob"""

    @pytest.fixture
    def job_factory(self):
        """Create job factory with Noop dependencies"""
        return RevenueReconJobFactory(
            notification_factory=NoopNotificationServiceFactory(),
            email_factory=NoopEmailServiceFactory(),
            jdbc_factory=NoopJdbcConnectionServiceFactory()
        )

    @pytest.fixture
    def valid_config(self):
        """Valid job configuration for testing"""
        return {
            "revenue_recon_job": {
                "alarm_service": {
                    "notification_service": "NOOP"
                },
                "success_service": {
                    "notification_service": "NOOP"
                },
                "email_service": {
                    "service_type": "NOOP"
                },
                "postgres_connection": {
                    "database_type": "POSTGRES",
                    "host": "localhost",
                    "port": 5432,
                    "database": "test_db",
                    "user": "test_user",
                    "password": "test_password"
                }
            }
        }

    def test_valid_parameters(self, job_factory, valid_config):
        """Test job creation and execution with valid parameters"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        assert job is not None
        
        # Test that execute_job works with valid dates
        result = job.execute_job(start_date="2023-01-01", end_date="2023-01-31")
        assert result is not None

    def test_end_date_before_start_date_fails(self, job_factory, valid_config):
        """Test that end_date before start_date raises ValueError in execute_job"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(ValueError, match="end_date cannot be before start_date"):
            job.execute_job(
                start_date="2023-01-31",
                end_date="2023-01-01"
            )

    def test_invalid_date_format_start_date(self, job_factory, valid_config):
        """Test that invalid start_date format raises ValueError in execute_job"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(ValueError, match="start_date must be formatted as 'YYYY-MM-DD'"):
            job.execute_job(
                start_date="invalid-date",
                end_date="2023-01-31"
            )

    def test_invalid_date_format_end_date(self, job_factory, valid_config):
        """Test that invalid end_date format raises ValueError in execute_job"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(ValueError, match="end_date must be formatted as 'YYYY-MM-DD'"):
            job.execute_job(
                start_date="2023-01-01",
                end_date="not-a-date"
            )

    def test_missing_distribution_list_parameter(self, job_factory, valid_config):
        """Test that missing distribution_list parameter raises ValueError"""
        with pytest.raises(ValueError, match="distribution_list must have at least one entry"):
            job_factory.create_job(
                from_addr="noreply@example.com",
                **valid_config
            )

    def test_empty_distribution_list_parameter(self, job_factory, valid_config):
        """Test that empty distribution_list parameter raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email address in distribution_list:"):
            job_factory.create_job(
                distribution_list="",
                from_addr="noreply@example.com",
                **valid_config
            )

    def test_missing_from_addr_parameter(self, job_factory, valid_config):
        """Test that missing from_addr parameter raises TypeError"""
        with pytest.raises(TypeError, match="expected string or bytes-like object"):
            job_factory.create_job(
                distribution_list="test@example.com",
                **valid_config
            )

    def test_invalid_email_format_distribution_list(self, job_factory, valid_config):
        """Test that invalid email format in distribution_list raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email address in distribution_list: invalid-email"):
            job_factory.create_job(
                distribution_list="invalid-email",
                from_addr="noreply@example.com",
                **valid_config
            )

    def test_invalid_email_format_from_addr(self, job_factory, valid_config):
        """Test that invalid email format in from_addr raises ValueError"""
        with pytest.raises(ValueError, match="from_addr must be a valid email address"):
            job_factory.create_job(
                distribution_list="test@example.com",
                from_addr="invalid-email",
                **valid_config
            )

    def test_multiple_emails_in_distribution_list(self, job_factory, valid_config):
        """Test that multiple valid emails in distribution_list work"""
        job = job_factory.create_job(
            distribution_list="test1@example.com,test2@example.com,test3@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        assert job is not None

    def test_invalid_email_in_multiple_distribution_list(self, job_factory, valid_config):
        """Test that one invalid email in multiple distribution_list raises ValueError"""
        with pytest.raises(ValueError, match="Invalid email address in distribution_list: invalid-email"):
            job_factory.create_job(
                distribution_list="test1@example.com,invalid-email,test3@example.com",
                from_addr="noreply@example.com",
                **valid_config
            )

    def test_missing_revenue_recon_job_config(self, job_factory):
        """Test that missing revenue_recon_job config raises ValueError"""
        with pytest.raises(ValueError, match="revenue_recon_job value must be a dict"):
            job_factory.create_job(
                distribution_list="test@example.com",
                from_addr="noreply@example.com"
            )

    def test_missing_postgres_connection_config(self, job_factory):
        """Test that missing postgres_connection config raises ValueError"""
        invalid_config = {
            "revenue_recon_job": {
                "alarm_service": {"notification_service": "NOOP"},
                "success_service": {"notification_service": "NOOP"},
                "email_service": {"service_type": "NOOP"}
            }
        }
        
        with pytest.raises(ValueError, match="Missing required configuration key"):
            job_factory.create_job(
                distribution_list="test@example.com",
                from_addr="noreply@example.com",
                **invalid_config
            )

    def test_missing_start_date_parameter(self, job_factory, valid_config):
        """Test that missing start_date parameter raises TypeError"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(TypeError, match="missing.*required.*argument.*start_date"):
            job.execute_job(end_date="2023-01-31")

    def test_missing_end_date_parameter(self, job_factory, valid_config):
        """Test that missing end_date parameter raises TypeError"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(TypeError, match="missing.*required.*argument.*end_date"):
            job.execute_job(start_date="2023-01-01")

    def test_empty_start_date_parameter(self, job_factory, valid_config):
        """Test that empty start_date parameter raises ValueError"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(ValueError, match="start_date is required"):
            job.execute_job(start_date="", end_date="2023-01-31")

    def test_empty_end_date_parameter(self, job_factory, valid_config):
        """Test that empty end_date parameter raises ValueError"""
        job = job_factory.create_job(
            distribution_list="test@example.com",
            from_addr="noreply@example.com",
            **valid_config
        )
        with pytest.raises(ValueError, match="end_date is required"):
            job.execute_job(start_date="2023-01-01", end_date="")