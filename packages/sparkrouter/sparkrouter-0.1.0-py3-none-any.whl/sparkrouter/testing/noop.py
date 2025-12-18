"""
Noop Testing Implementations
============================

No-operation implementations of service interfaces for testing.

These implementations allow testing jobs without mocks by providing
real objects that satisfy interfaces but don't perform actual I/O.

Philosophy:
    - Noop implementations preserve validation logic
    - Only the actual I/O operation is skipped
    - This allows testing business logic without external dependencies

Example:
    def test_my_job():
        job = MyJob(
            notification_service=NoopNotificationService()
        )
        result = job.run(input_path="/test", output_path="/out")
        assert result["status"] == "success"
"""

from sparkrouter.services.notification import NotificationService


class NoopNotificationService(NotificationService):
    """
    No-operation notification service for testing.

    Records all notifications sent for later assertions but doesn't
    perform any actual notification delivery.

    Example:
        notifier = NoopNotificationService()
        job = MyJob(notification_service=notifier)
        job.run()

        # Assert notifications were triggered
        assert len(notifier.notifications) == 1
        assert "Success" in notifier.notifications[0]["subject"]
    """

    def __init__(self):
        self.notifications = []

    def send_notification(self, subject: str, message: str) -> bool:
        """
        Record the notification without sending.

        Args:
            subject: Notification subject.
            message: Notification message.

        Returns:
            Always returns True.
        """
        self.notifications.append({
            "subject": subject,
            "message": message,
        })
        print(f"NOOP: Would send notification - Subject: {subject}")
        return True

    def clear(self) -> None:
        """Clear recorded notifications."""
        self.notifications = []
