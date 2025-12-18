"""Tests for noop testing implementations."""

import pytest

from sparkrouter.services.notification import NotificationService
from sparkrouter.testing.noop import NoopNotificationService


class TestNoopNotificationService:
    """Tests for NoopNotificationService."""

    def test_implements_notification_service(self):
        service = NoopNotificationService()
        assert isinstance(service, NotificationService)

    def test_send_notification_returns_true(self):
        service = NoopNotificationService()
        result = service.send_notification(
            subject="Test Subject",
            message="Test Message"
        )
        assert result is True

    def test_send_notification_records_notification(self):
        service = NoopNotificationService()
        service.send_notification(
            subject="Test Subject",
            message="Test Message"
        )
        assert len(service.notifications) == 1
        assert service.notifications[0]["subject"] == "Test Subject"
        assert service.notifications[0]["message"] == "Test Message"

    def test_records_multiple_notifications(self):
        service = NoopNotificationService()
        service.send_notification(subject="First", message="Message 1")
        service.send_notification(subject="Second", message="Message 2")
        service.send_notification(subject="Third", message="Message 3")
        assert len(service.notifications) == 3
        assert service.notifications[0]["subject"] == "First"
        assert service.notifications[1]["subject"] == "Second"
        assert service.notifications[2]["subject"] == "Third"

    def test_clear_removes_all_notifications(self):
        service = NoopNotificationService()
        service.send_notification(subject="Test", message="Message")
        service.send_notification(subject="Test2", message="Message2")
        assert len(service.notifications) == 2

        service.clear()
        assert len(service.notifications) == 0

    def test_can_be_used_in_job(self):
        """Test that NoopNotificationService works in a real job context."""
        from sparkrouter import AbstractJob
        from typing import Any

        class JobWithNotification(AbstractJob):
            def __init__(self, notifier: NotificationService):
                self.notifier = notifier

            def execute_job(self, **kwargs) -> dict:
                return {"status": "done"}

            def on_success(self, results: Any) -> None:
                self.notifier.send_notification(
                    subject="Job Success",
                    message=f"Completed with: {results}"
                )

            def on_failure(self, error_message: str) -> None:
                self.notifier.send_notification(
                    subject="Job Failed",
                    message=error_message
                )

        notifier = NoopNotificationService()
        job = JobWithNotification(notifier=notifier)
        job.run()

        assert len(notifier.notifications) == 1
        assert notifier.notifications[0]["subject"] == "Job Success"
        assert "done" in notifier.notifications[0]["message"]
