from abc import ABC, abstractmethod


class NotificationService(ABC):
    """
    Abstract Class for sending notifications
    """

    def __init__(self):
        pass

    @abstractmethod
    def send_notification(self, subject: str, message: str) -> bool:
        """
        Send a notification with the given subject and message.

        Args:
            subject: Notification subject
            message: Notification message

        Returns:
            True if notification was sent successfully, False otherwise
        """
        #  todo: raise exception if not implemented
        pass


class NoopNotificationService(NotificationService):
    """
    No-op notifier that does nothing when send_notification is called.
    Useful for disabling notifications in certain environments.
    """

    def send_notification(self, subject: str, message: str) -> bool:
        """
        Do nothing and return True.

        Args:
            subject: Notification subject
            message: Notification message

        Returns:
            Always returns True
        """
        print("No-op notifier: notification not sent")
        return True


class SNSNotificationService(NotificationService):
    """
    Class for sending notifications via AWS SNS.
    """

    def __init__(self, region: str, topic_arn: str):
        import boto3
        self.topic_arn = topic_arn
        self.sns_client = boto3.client('sns', region_name=region)

    #     todo: topic_arn goes here
    def send_notification(self, subject: str, message: str) -> bool:
        """
        Send an SNS notification.

        Args:
            subject: Notification subject
            message: Notification message

        Returns:
            True if notification was sent successfully, False otherwise
        """
        try:
            response = self.sns_client.publish(
                TopicArn=self.topic_arn,
                Message=message,
                Subject=subject
            )
            print(f"SNS notification sent to {self.topic_arn}: {response}")
            return True
        except Exception as sns_error:
            print(f"Failed to send SNS notification to {self.topic_arn}: {str(sns_error)}")
            return False
