from dwh.jobs.abstract_job_factory import AbstractJobFactory
from dwh.jobs.generic_example.generic_example_job import GenericExampleJob
from dwh.services.notification.notification_service_factory import NotificationServiceFactory


class GenericExampleJobFactory(AbstractJobFactory):
    """
    Factory for creating GenericExampleJob instances.
    """
    
    def __init__(
            self,
            notification_service_factory=None,
            **kwargs
    ):
        """
        Initialize the factory with dependencies.
        
        :param notification_service_factory: Factory for creating notification services
        :param kwargs: Additional arguments
        """
        super().__init__(**kwargs)
        self.notification_service_factory = notification_service_factory or NotificationServiceFactory

    def create_job(self, **kwargs) -> GenericExampleJob:
        """
        Create a GenericExampleJob instance.
        
        :param kwargs: Job configuration parameters
        :return: GenericExampleJob instance
        """
        # Extract job specific configuration, ensure it is well-formed Dictionary
        config = self.parse_job_config(job_name='generic_example_job', **kwargs)
        print("Configuration for GenericExampleJob:", config)
        if not config:
            raise ValueError("Configuration for 'generic_example_job' is required.")

        try:
            alarm_config = config['alarm_service']
            alarm_service = self.notification_service_factory.create_notification_service(config=alarm_config)

            return GenericExampleJob(
                alarm_service=alarm_service,
            )
        except KeyError as e:
            # todo: utility to display configuration expectations
            raise ValueError(f"Missing required configuration key: {e}")


def main(**kwargs):
    # Create and run the job
    operator = GenericExampleJobFactory(**kwargs)
    return operator.run(**kwargs)
