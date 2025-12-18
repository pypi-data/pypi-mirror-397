from typing import Dict, Any

from dwh.services.event.job_event_publisher import (
    JobEventPublisher,
    SNSJobEventPublisher,
    NoopJobEventPublisher
)


class JobEventPublisherFactory:
    """
    Factory class for creating instances of JobEventPublisher.

    Configuration is passed via a dictionary with the following structure:

    For SNS event publisher:
    {
        'publisher_type': 'SNS',
        'region': 'us-west-1',
        'topic_arn': 'arn:aws:sns:us-west-1:123456789012:job-events'
    }

    For NOOP event publisher:
    {
        'publisher_type': 'NOOP'
    }
    """

    @staticmethod
    def _get_publisher_type(config: Dict[str, Any]) -> str:
        publisher_type = config.get('publisher_type')
        if not publisher_type:
            valid_types = ['SNS', 'NOOP']
            raise ValueError(
                f"Missing publisher_type. Valid options are: {', '.join(valid_types)}")
        return publisher_type.strip().upper()

    @staticmethod
    def create_job_event_publisher(config: Dict[str, Any]) -> JobEventPublisher:
        """
        Creates and returns an instance of JobEventPublisher based on configuration.

        Args:
            config: Dictionary containing the configuration parameters

        Returns:
            A concrete implementation of JobEventPublisher

        Raises:
            ValueError: If required parameters are missing or invalid
        """
        print("JobEventPublisher Configuration:", config)

        publisher_type = JobEventPublisherFactory._get_publisher_type(config)

        if publisher_type == 'NOOP':
            return NoopJobEventPublisher()
        elif publisher_type == 'SNS':
            region = config.get('region')
            if not region:
                raise ValueError("region is required when using SNS event publisher")
            topic_arn = config.get('topic_arn')
            if not topic_arn:
                raise ValueError("topic_arn is required when using SNS event publisher")
            return SNSJobEventPublisher(region=region, topic_arn=topic_arn)
        else:
            valid_types = ['SNS', 'NOOP']
            raise ValueError(
                f"Unsupported publisher_type[{publisher_type}]. Valid options are: {', '.join(valid_types)}")
