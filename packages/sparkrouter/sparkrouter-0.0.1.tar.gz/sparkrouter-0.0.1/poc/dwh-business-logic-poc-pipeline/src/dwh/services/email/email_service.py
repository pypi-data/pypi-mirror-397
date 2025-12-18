from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
import smtplib
from typing import List


class EmailService(ABC):
    """
    Abstract Class for sending emails
    """

    def __init__(self):
        pass

    @abstractmethod
    def send_email(self, msg: MIMEMultipart, from_addr: str, bcc_addr: List[str]) -> bool:
        """
        Send a notification with the given subject and message.

        Args:
            msg: MIMEMultipart message object containing the email content
            from_addr: Sender's email address
            bcc_addr: List of BCC email addresses

        Returns:
            True if notification was sent successfully, False otherwise
        """
        #  todo: raise exception if not implemented
        pass


class NoopEmailService(EmailService):
    """
    No-op implementation of EmailService that does nothing
    """

    def __init__(self):
        super().__init__()

    def send_email(self, msg: MIMEMultipart, from_addr: str, bcc_addr: List[str]) -> bool:
        print(f"NOOP EmailService! From: {from_addr}, BCC: {', '.join(bcc_addr)}, Message content:", msg.as_string())
        # No operation performed
        return True


class SMTPEmailService(EmailService):
    """
    Concrete implementation of EmailService using SMTP
    """

    def __init__(self, smtp_server: str, smtp_port: int, username=None, password=None):
        super().__init__()
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, msg: MIMEMultipart, from_addr: str, bcc_addr: List[str]) -> bool:
        server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        try:
            if self.username and self.password:
                server.login(user=self.username, password=self.password)

            server.ehlo()
            if server.has_extn('STARTTLS'):
                server.starttls()
                server.ehlo()
            text = msg.as_string()
            server.sendmail(from_addr, bcc_addr, text)
        except Exception as e:
            print("Exception in Sending email" + str(e))
            raise Exception(f"Failed to send email: {str(e)}")
        finally:
            server.quit()

        return True


class SESEmailService(EmailService):
    """
    Concrete implementation of EmailService using SMTP
    """

    def __init__(self, region: str):
        super().__init__()
        import boto3
        self.ses = boto3.client('ses', region_name=region)

    def send_email(self, msg: MIMEMultipart, from_addr: str, bcc_addr: List[str]) -> bool:
        try:
            response = self.ses.send_raw_email(
                Source=from_addr,
                Destinations=bcc_addr,
                RawMessage={'Data': msg.as_string()}
            )
            print(f"Email sent! Message ID: {response['MessageId']}")
            return True
        except Exception as e:
            print("Exception in Sending email" + str(e))
            raise Exception(f"Failed to send email: {str(e)}")
