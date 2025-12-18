import json

import pytest
from dwh.services.notification.notification_service_factory import NotificationServiceFactory
from dwh.services.notification.notification_service import NoopNotificationService


class TestNotificationServiceFactory:

    def test_create_noop_notification_service(self):
        # Act
        result = NotificationServiceFactory.create_notification_service({
            'notification_service': 'NOOP',
        })

        # Assert
        assert isinstance(result, NoopNotificationService)

    def test_create_sns_notification_service_without_topic_arn_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="topic_arn is required when using SNS notification service"):
            NotificationServiceFactory.create_notification_service({
                'region': 'us-west-2',
                'notification_service': 'SNS'
            })

    def test_create_notification_service_with_invalid_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError,
                           match="Unsupported notification_service\\[INVALID\\]. Valid options are: SNS, NOO"):
            NotificationServiceFactory.create_notification_service({
                'notification_service': 'INVALID'
            })

    def test_create_notification_service_with_none_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="Missing notification_service. Valid options are: SNS, NOOP"):
            NotificationServiceFactory.create_notification_service({
                'notification_service': None
            })

    def test_sns_service_requires_topic_arn_parameter(self):
        # Test that the factory validates required SNS parameters
        # Act & Assert
        with pytest.raises(ValueError, match="topic_arn is required"):
            NotificationServiceFactory.create_notification_service({
                'notification_service': 'SNS',
                'region': 'us-west-2'
            })

    def test_factory_accepts_unknown_kwargs_without_error(self):
        # Test that the factory doesn't break with extra parameters
        # Act
        result = NotificationServiceFactory.create_notification_service({
            'notification_service': 'NOOP',
            'extra_param': 'should_be_ignored',
            'another_param': 123
        })

        # Assert
        assert isinstance(result, NoopNotificationService)
