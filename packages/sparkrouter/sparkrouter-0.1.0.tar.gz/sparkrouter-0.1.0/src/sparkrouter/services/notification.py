"""
Notification Service Interface
==============================

Abstract interface for notification services used by jobs to report
success, failure, or other events.
"""

from abc import ABC, abstractmethod


class NotificationService(ABC):
    """
    Abstract base class for notification services.

    Implement this interface to create custom notification handlers
    for SNS, email, Slack, PagerDuty, etc.

    Example:
        class SlackNotificationService(NotificationService):
            def __init__(self, webhook_url: str):
                self.webhook_url = webhook_url

            def send_notification(self, subject: str, message: str) -> bool:
                response = requests.post(self.webhook_url, json={
                    "text": f"*{subject}*\\n{message}"
                })
                return response.status_code == 200
    """

    @abstractmethod
    def send_notification(self, subject: str, message: str) -> bool:
        """
        Send a notification with the given subject and message.

        Args:
            subject: Notification subject/title.
            message: Notification body/content.

        Returns:
            True if notification was sent successfully, False otherwise.

        Raises:
            May raise exceptions for critical failures that should
            halt job execution.
        """
        raise NotImplementedError("Subclasses must implement send_notification()")
