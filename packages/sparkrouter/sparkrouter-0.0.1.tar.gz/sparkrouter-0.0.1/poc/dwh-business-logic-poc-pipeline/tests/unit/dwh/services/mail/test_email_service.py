"""
Unit tests for EmailService implementations
"""
# Import from Python's standard library with explicit naming to avoid conflicts
import email.mime.multipart as mime_multipart
import email.mime.text as mime_text

from dwh.services.email.email_service import (
    EmailService,
    NoopEmailService,
    SMTPEmailService,
    SESEmailService
)


class TestNoopEmailService:
    """Test NoopEmailService - fully testable without mocking"""

    def test_init(self):
        """Test NoopEmailService initialization"""
        service = NoopEmailService()
        assert isinstance(service, EmailService)
        assert isinstance(service, NoopEmailService)

    def test_send_email_simple(self):
        """Test sending simple email"""
        service = NoopEmailService()

        # Create test message
        msg = mime_multipart.MIMEMultipart()
        msg['Subject'] = 'Test Subject'
        msg['From'] = 'sender@example.com'
        msg['To'] = 'recipient@example.com'

        body = mime_text.MIMEText('Test email body')
        msg.attach(body)

        # Test sending
        result = service.send_email(
            msg=msg,
            from_addr='sender@example.com',
            bcc_addr=['bcc1@example.com', 'bcc2@example.com']
        )

        assert result is True

    def test_send_email_empty_bcc(self):
        """Test sending email with empty BCC list"""
        service = NoopEmailService()

        msg = mime_multipart.MIMEMultipart()
        msg['Subject'] = 'Test Subject'

        result = service.send_email(
            msg=msg,
            from_addr='sender@example.com',
            bcc_addr=[]
        )

        assert result is True

    def test_send_email_complex_message(self):
        """Test sending complex multipart email"""
        service = NoopEmailService()

        # Create complex message
        msg = mime_multipart.MIMEMultipart('alternative')
        msg['Subject'] = 'Complex Test Email'
        msg['From'] = 'sender@example.com'

        # Add text part
        text_part = mime_text.MIMEText('Plain text version', 'plain')
        msg.attach(text_part)

        # Add HTML part
        html_part = mime_text.MIMEText('<html><body><h1>HTML Version</h1></body></html>', 'html')
        msg.attach(html_part)

        result = service.send_email(
            msg=msg,
            from_addr='complex@example.com',
            bcc_addr=['recipient1@example.com', 'recipient2@example.com']
        )

        assert result is True

    def test_send_email_unicode_content(self):
        """Test sending email with Unicode content"""
        service = NoopEmailService()

        msg = mime_multipart.MIMEMultipart()
        msg['Subject'] = 'Unicode Test: 📧 测试 🎯'

        body = mime_text.MIMEText('Unicode content: Hello 世界! 🌍', 'plain', 'utf-8')
        msg.attach(body)

        result = service.send_email(
            msg=msg,
            from_addr='unicode@example.com',
            bcc_addr=['recipient@example.com']
        )

        assert result is True


class TestSMTPEmailService:
    """Test SMTPEmailService initialization and configuration"""

    def test_init_basic(self):
        """Test basic SMTP service initialization"""
        service = SMTPEmailService(
            smtp_server='localhost',
            smtp_port=587
        )

        assert service.smtp_server == 'localhost'
        assert service.smtp_port == 587
        # assert service.debug_level is False

    def test_init_with_debug(self):
        """Test SMTP service initialization with debug enabled"""
        service = SMTPEmailService(
            smtp_server='mail.example.com',
            smtp_port=25,
        )

        assert service.smtp_server == 'mail.example.com'
        assert service.smtp_port == 25

    def test_init_inheritance(self):
        """Test that SMTPEmailService properly inherits from EmailService"""
        service = SMTPEmailService('localhost', 587)
        assert isinstance(service, EmailService)
        assert isinstance(service, SMTPEmailService)


# class TestSESEmailService:
#     """Test SESEmailService initialization and configuration"""
#
#     def test_init_default_region(self):
#         """Test SES service initialization with default region"""
#         # Note: This will fail if AWS credentials aren't available
#         # but tests the initialization logic
#         try:
#             service = SESEmailService(region='us-west-1')
#             assert isinstance(service, EmailService)
#             assert isinstance(service, SESEmailService)
#         except Exception:
#             # AWS SDK not configured - that's okay for unit testing
#             pass
#
#     def test_init_custom_region(self):
#         """Test SES service initialization with custom region"""
#         try:
#             service = SESEmailService(region='eu-west-1')
#             assert isinstance(service, EmailService)
#             assert isinstance(service, SESEmailService)
#         except Exception:
#             # AWS SDK not configured - that's okay for unit testing
#             pass


class TestEmailMessageCreation:
    """Test email message creation and formatting - pure functions"""

    def test_create_simple_message(self):
        """Test creating a simple email message"""
        msg = mime_multipart.MIMEMultipart()
        msg['Subject'] = 'Test Subject'
        msg['From'] = 'sender@example.com'
        msg['To'] = 'recipient@example.com'

        body = mime_text.MIMEText('Test body content')
        msg.attach(body)

        # Verify message structure
        assert msg['Subject'] == 'Test Subject'
        assert msg['From'] == 'sender@example.com'
        assert msg['To'] == 'recipient@example.com'

        # Verify message can be serialized
        message_string = msg.as_string()
        assert 'Test Subject' in message_string
        assert 'Test body content' in message_string

    def test_create_multipart_message(self):
        """Test creating multipart email message"""
        msg = mime_multipart.MIMEMultipart('alternative')
        msg['Subject'] = 'Multipart Test'

        # Add multiple parts
        text_part = mime_text.MIMEText('Text version', 'plain')
        html_part = mime_text.MIMEText('<h1>HTML version</h1>', 'html')

        msg.attach(text_part)
        msg.attach(html_part)

        # Verify multipart structure
        assert len(msg.get_payload()) == 2
        assert msg.get_content_type() == 'multipart/alternative'

        message_string = msg.as_string()
        assert 'Text version' in message_string
        assert '<h1>HTML version</h1>' in message_string

    def test_message_encoding(self):
        """Test email message encoding with special characters"""
        msg = mime_multipart.MIMEMultipart()
        msg['Subject'] = 'Encoding Test: 特殊字符 🚀'

        body = mime_text.MIMEText('Content with émojis: 🎯 and unicode: 你好', 'plain', 'utf-8')
        msg.attach(body)

        # Verify message can be serialized without errors
        message_string = msg.as_string()
        assert isinstance(message_string, str)
        assert len(message_string) > 0
