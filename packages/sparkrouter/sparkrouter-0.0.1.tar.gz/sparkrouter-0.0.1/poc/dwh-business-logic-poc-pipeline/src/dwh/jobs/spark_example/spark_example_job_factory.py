from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.spark_example.spark_example_job import SparkExampleJob
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.spark.spark_session_factory import SparkSessionFactory


class SparkExampleJobFactory(AbstractJobFactory):
    """
    Factory for creating SparkExampleJob instances.
    """
    
    def __init__(
            self,
            notification_factory=None,
            spark_factory=None,
            **kwargs
    ):
        """Initialize with optional factory dependencies."""
        super().__init__(**kwargs)
        self.notification_factory = notification_factory or NotificationServiceFactory
        self.spark_factory = spark_factory or SparkSessionFactory

    def create_job(self, **kwargs) -> SparkExampleJob:
        """Create a SparkExampleJob with the specified configuration."""
        config = self.parse_job_config(job_name='spark_example_job', **kwargs)
        print("Configuration for SparkExampleJob:", config)

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

            # Create Spark session
            has_spark = kwargs.get('has_spark', False)
            if isinstance(has_spark, str):
                has_spark = has_spark.lower() in ['true', '1', 'yes']
            print(f"Has Spark: {has_spark}")

            if not has_spark:
                raise ValueError("Spark session is required for SparkExampleJob.")

            spark_session = self.spark_factory.create_spark_session(**kwargs)

            # Create and return the job
            return SparkExampleJob(
                alarm_service=alarm_service,
                success_service=success_service,
                spark_session=spark_session,
            )
        except KeyError as e:
            raise ValueError(f"Missing required configuration key: {e}")


def main(**kwargs):
    """
    Entrypoint for SparkExample job.
    """
    operator = SparkExampleJobFactory(**kwargs)
    return operator.run(**kwargs)
