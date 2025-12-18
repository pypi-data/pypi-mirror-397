import pytest
from dwh.services.email.email_service_factory import EmailServiceFactory
from dwh.services.email.email_service import NoopEmailService


class TestEmailServiceFactory:

    def test_create_noop_email_service(self):
        # Act
        result = EmailServiceFactory.create_email_service({
            'service_type': 'NOOP'
        })

        # Assert
        assert isinstance(result, NoopEmailService)

    def test_create_email_service_invalid_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError,
                           match="Unsupported email service_type\\[INVALID\\]. Valid options are: SES, SMTP, NOOP"):
            EmailServiceFactory.create_email_service({
                'service_type': 'INVALID'
            })

    def test_create_email_service_none_type_raises_error(self):
        # Act & Assert
        with pytest.raises(ValueError, match="Missing email service_type. Valid options are: SES, SMTP, NOOP"):
            EmailServiceFactory.create_email_service({
                'service_type': None
            })

    def test_create_email_service_empty_kwargs_raises_error(self):
        # Act & Assert
        with pytest.raises(TypeError):
            EmailServiceFactory.create_email_service()

    def test_factory_accepts_unknown_kwargs_without_error(self):
        # Test that the factory doesn't break with extra parameters
        # Act
        result = EmailServiceFactory.create_email_service({
            'service_type': 'NOOP',
            'extra_param': 'should_be_ignored',
            'another_param': 123
        })

        # Assert
        assert isinstance(result, NoopEmailService)
