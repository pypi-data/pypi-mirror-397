from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.revenue_recon.revenue_recon_job import RevenueReconJob
from dwh.services.database.jdbc.jdbc_connection_service_factory import JdbcConnectionServiceFactory
from dwh.services.email.email_service_factory import EmailServiceFactory
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.spark.spark_session_factory import SparkSessionFactory


class RevenueReconJobFactory(AbstractJobFactory):
    """
    Factory for creating RevenueReconJob instances.
    """
    
    def __init__(self,
                 notification_factory=None,
                 email_factory=None,
                 jdbc_factory=None,
                 spark_factory=None,
                 **kwargs):
        """Initialize with optional factory dependencies."""
        super().__init__(**kwargs)
        self.notification_factory = notification_factory or NotificationServiceFactory
        self.email_factory = email_factory or EmailServiceFactory
        self.jdbc_factory = jdbc_factory or JdbcConnectionServiceFactory
        self.spark_factory = spark_factory or SparkSessionFactory

    def create_job(self, **kwargs) -> RevenueReconJob:
        """Create a RevenueReconJob with the specified configuration."""
        config = self.parse_job_config(job_name='revenue_recon_job', **kwargs)
        print("Configuration for RevenueReconJob:", config)

        try:
            # Create notification services
            alarm_config = config['alarm_service']
            alarm_service = self.notification_factory.create_notification_service(
                config=alarm_config
            )

            success_config = config['success_service']
            success_service = self.notification_factory.create_notification_service(
                config=success_config
            )

            # Create email service
            email_config = config['email_service']
            email_service = self.email_factory.create_email_service(config=email_config)

            # Create Spark session if needed
            has_spark = kwargs.get('has_spark', False)
            spark_session = None
            if isinstance(has_spark, str):
                has_spark = has_spark.lower() in ['true', '1', 'yes']

            # Create database connection
            postgres_config = config['postgres_connection']
            if has_spark and not postgres_config.get('force_direct_connection', False):
                spark_session = self.spark_factory.create_spark_session(**kwargs)

            postgres_service = self.jdbc_factory.create_connection(
                config=postgres_config,
                spark_session=spark_session,
            )

            # Create and return the job
            return RevenueReconJob(
                alarm_service=alarm_service,
                success_service=success_service,
                email_service=email_service,
                postgres_service=postgres_service,
                distribution_list=kwargs.get('distribution_list'),
                from_addr=kwargs.get('from_addr'),
            )
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")


def main(**kwargs):
    """
    Entrypoint for RevenueRecon job.
    """
    operator = RevenueReconJobFactory(**kwargs)
    return operator.run(**kwargs)
