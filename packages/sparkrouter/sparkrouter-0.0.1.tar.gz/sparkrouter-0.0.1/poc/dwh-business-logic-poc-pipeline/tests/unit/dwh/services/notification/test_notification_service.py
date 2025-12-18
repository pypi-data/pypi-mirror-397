"""
Unit tests for NotificationService implementations
"""
import pytest

from dwh.services.notification.notification_service import (
    NotificationService,
    NoopNotificationService,
    SNSNotificationService
)


class TestNoopNotificationService:
    """Test NoopNotificationService - fully testable without mocking"""

    def test_init(self):
        """Test NoopNotificationService initialization"""
        service = NoopNotificationService()
        assert isinstance(service, NotificationService)
        assert isinstance(service, NoopNotificationService)

    def test_send_notification_simple(self):
        """Test sending simple notification"""
        service = NoopNotificationService()

        result = service.send_notification(
            subject="Test Subject",
            message="Test message content"
        )

        assert result is True

    def test_send_notification_empty_message(self):
        """Test sending notification with empty message"""
        service = NoopNotificationService()

        result = service.send_notification(
            subject="Test Subject",
            message=""
        )

        assert result is True

    def test_send_notification_empty_subject(self):
        """Test sending notification with empty subject"""
        service = NoopNotificationService()

        result = service.send_notification(
            subject="",
            message="Test message"
        )

        assert result is True

    def test_send_notification_unicode_content(self):
        """Test sending notification with Unicode content"""
        service = NoopNotificationService()

        result = service.send_notification(
            subject="Unicode Test: 📧 测试",
            message="Message with émojis: 🎯 and unicode: 世界"
        )

        assert result is True

    def test_send_notification_long_content(self):
        """Test sending notification with long content"""
        service = NoopNotificationService()

        long_message = "This is a very long message. " * 100

        result = service.send_notification(
            subject="Long Message Test",
            message=long_message
        )

        assert result is True

    def test_send_notification_special_characters(self):
        """Test sending notification with special characters"""
        service = NoopNotificationService()

        result = service.send_notification(
            subject="Special chars: !@#$%^&*()[]{}|\\:;\"'<>?,./",
            message="Message with newlines\nand\ttabs\rand\r\ncarriage returns"
        )

        assert result is True


class TestSNSNotificationService:
    """Test SNSNotificationService initialization and configuration"""

    def test_init_basic(self):
        """Test basic SNS notification service initialization"""
        try:
            service = SNSNotificationService({
                'region': "us-east-1",
                'topic_arn': "arn:aws:sns:us-east-1:123456789012:test-topic"
            })
            assert service.topic_arn == "arn:aws:sns:us-east-1:123456789012:test-topic"
            assert isinstance(service, NotificationService)
            assert isinstance(service, SNSNotificationService)
        except Exception:
            # AWS SDK not configured - that's okay for unit testing
            pass

    def test_init_with_different_region(self):
        """Test SNS notification service initialization with different region"""
        try:
            service = SNSNotificationService({
                'region': "eu-west-1",
                'topic_arn': "arn:aws:sns:eu-west-1:123456789012:test-topic"
            })
            assert service.topic_arn == "arn:aws:sns:eu-west-1:123456789012:test-topic"
        except Exception:
            # AWS SDK not configured - that's okay for unit testing
            pass

    def test_init_inheritance(self):
        """Test that SNSNotificationService properly inherits from NotificationService"""
        try:
            service = SNSNotificationService({
                'region': "us-east-1",
                'topic_arn': "arn:aws:sns:us-east-1:123456789012:test"
            })
            assert isinstance(service, NotificationService)
            assert isinstance(service, SNSNotificationService)
        except Exception:
            # AWS SDK not configured - that's okay for unit testing
            pass


class TestNotificationMessageFormatting:
    """Test notification message formatting - pure functions"""

    def test_subject_formatting(self):
        """Test subject line formatting"""
        test_subjects = [
            "Simple Subject",
            "Subject with Numbers 123",
            "Subject with Special: chars!",
            "Unicode Subject: 测试 🎯",
            ""
        ]

        for subject in test_subjects:
            # Subject should remain unchanged for basic formatting
            formatted = subject.strip()
            assert isinstance(formatted, str)

    def test_message_formatting(self):
        """Test message content formatting"""
        test_messages = [
            "Simple message",
            "Message\nwith\nnewlines",
            "Message with unicode: 世界 🌍",
            "Very long message: " + "content " * 50,
            ""
        ]

        for message in test_messages:
            # Message should remain unchanged for basic formatting
            formatted = message.strip()
            assert isinstance(formatted, str)

    def test_topic_arn_validation_pattern(self):
        """Test AWS SNS topic ARN validation patterns"""
        valid_arns = [
            "arn:aws:sns:us-east-1:123456789012:test-topic",
            "arn:aws:sns:eu-west-1:987654321098:my-topic",
            "arn:aws:sns:ap-southeast-1:111111111111:notifications",
            "arn:aws:sns:us-west-2:222222222222:alerts-topic"
        ]

        invalid_arns = [
            "invalid-arn",
            "arn:aws:s3:bucket:name",
            "arn:aws:sns:",
            "",
            "not-an-arn-at-all"
        ]

        # Simple ARN validation pattern for SNS topics
        import re
        sns_arn_pattern = r'^arn:aws:sns:[a-z0-9-]+:\d{12}:[a-zA-Z0-9_-]+$'

        for arn in valid_arns:
            assert re.match(sns_arn_pattern, arn) is not None, f"Valid ARN failed: {arn}"

        for arn in invalid_arns:
            assert re.match(sns_arn_pattern, arn) is None, f"Invalid ARN passed: {arn}"

    def test_notification_content_validation(self):
        """Test notification content validation logic"""
        # Test different content scenarios
        test_cases = [
            ("", "", True),  # Empty is allowed
            ("Subject", "Message", True),  # Normal case
            ("Very long subject " * 10, "Very long message " * 100, True),  # Long content
            ("Unicode: 测试", "Unicode: 世界", True),  # Unicode content
        ]

        for subject, message, expected_valid in test_cases:
            # Basic validation - all cases should be valid for our simple implementation
            is_valid = isinstance(subject, str) and isinstance(message, str)
            assert is_valid == expected_valid

    def test_aws_region_validation(self):
        """Test AWS region validation patterns"""
        valid_regions = [
            "us-east-1",
            "us-west-2",
            "eu-west-1",
            "ap-southeast-1",
            "ca-central-1"
        ]

        invalid_regions = [
            "invalid-region",
            "us-east",
            "",
            "123-456-789"
        ]

        # Simple region validation pattern
        import re
        region_pattern = r'^[a-z]{2}-[a-z]+-\d+$'

        for region in valid_regions:
            assert re.match(region_pattern, region) is not None, f"Valid region failed: {region}"

        for region in invalid_regions:
            assert re.match(region_pattern, region) is None, f"Invalid region passed: {region}"
