from typing import Dict, Any

from dwh.services.notification.notification_service import (
    SNSNotificationService,
    NoopNotificationService,
    NotificationService
)


class NotificationServiceFactory:
    """
    Factory class for creating instances of NotificationService.
    
    The NotificationServiceFactory implements the factory design pattern to create
    different types of notification services based on configuration parameters.
    
    Currently supported notification service types:
    - SNS: Amazon Simple Notification Service for sending notifications to subscribed endpoints
    - NOOP: No-operation service that logs messages but doesn't send actual notifications
           (useful for testing or environments where notifications should be disabled)
    
    Configuration is passed via a dictionary with the naming convention:
    '{notification_name}_notification_service'
    
    Example usage:
    ```python
    # Create an SNS notification service
    sns_config = {
        'alarm_notification_service': {
            'service_type': 'SNS',
            'region': 'us-west-1',
            'topic_arn': 'arn:aws:sns:us-west-1:123456789012:alarm-topic'
        }
    }
    notification_service = NotificationServiceFactory.create_notification_service(
        'alarm', **sns_config
    )
    
    # Create a NOOP notification service
    noop_config = {
        'alert_notification_service': {
            'service_type': 'NOOP'
        }
    }
    notification_service = NotificationServiceFactory.create_notification_service(
        'alert', **noop_config
    )
    ```
    """

    @staticmethod
    def _get_service_type(config: Dict[str, Any]) -> str:
        type = config.get('notification_service')
        if not type:
            valid_types = ['SNS', 'NOOP']
            raise ValueError(
                f"Missing notification_service. Valid options are: {', '.join(valid_types)}")
        type = type.strip().upper()

        return type

    @staticmethod
    def create_notification_service(config: Dict[str, Any]) -> NotificationService:
        """
        Creates and returns an instance of NotificationService based on configuration.
        
        This method looks for a configuration parameter with the key format:
        '{notification_name}_notification_service'
        
        The configuration can be either a dictionary or a JSON string with the following structure:
        
        For SNS notification service:
        {
            'service_type': 'SNS',           # Required: Must be 'SNS' (case-insensitive)
            'region': 'us-west-1',           # Optional: AWS region (defaults to 'us-west-1')
            'topic_arn': '[TOPIC_ARN]'       # Required: The ARN of the SNS topic
        }
        
        For NOOP notification service:
        {
            'service_type': 'NOOP'           # Required: Must be 'NOOP' (case-insensitive)
        }
        
        Args:
            notification_name (str): Name identifier for the notification service
                                    (used to find the corresponding configuration)
            **kwargs: Dictionary containing the configuration parameters
        
        Returns:
            A concrete implementation of NotificationService (SNSNotificationService or NoopNotificationService)
        
        Raises:
            ValueError: If required parameters are missing or invalid
                       (notification_name, service_type, topic_arn for SNS)
            ValueError: If an unsupported service_type is specified
            ValueError: If the JSON string cannot be parsed
        """
        print("NotificationService Configuration:", config)

        type = NotificationServiceFactory._get_service_type(config=config)
        if type == 'NOOP':
            return NoopNotificationService()
        elif type == 'SNS':
            sns_region = config.get('region')
            if not sns_region:
                raise ValueError("region is required when using SNS notification service")
            topic_arn = config.get('topic_arn')
            if not topic_arn:
                # todo: show all expected parameters in the error message
                raise ValueError("topic_arn is required when using SNS notification service")
            return SNSNotificationService(region=sns_region, topic_arn=topic_arn)
        else:
            # List all available notification service types
            valid_types = ['SNS', 'NOOP']
            raise ValueError(
                f"Unsupported notification_service[{type}]. Valid options are: {', '.join(valid_types)}")
