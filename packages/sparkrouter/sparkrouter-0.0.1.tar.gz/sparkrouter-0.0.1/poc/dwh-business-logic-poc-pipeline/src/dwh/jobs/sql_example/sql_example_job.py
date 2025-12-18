import re
from importlib.resources import files
from datetime import datetime
from typing import Union

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dwh.jobs.abstract_job import AbstractJob
from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService
from dwh.services.email.email_service import EmailService
from dwh.services.notification.notification_service import NotificationService


class SQLExampleJob(AbstractJob):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    # tellme: be explicit about parameters and their types. DO NOT USE **ARGS OR **KWARGS
    def __init__(
            self,
            alarm_service: NotificationService,
            email_service: EmailService,
            postgres_service: JdbcConnectionService,
            distribution_list: Union[list, str],
            from_addr: str,
    ):
        if not isinstance(alarm_service, NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        if not isinstance(email_service, EmailService):
            raise ValueError("email_service must be an instance of EmailService")

        if not isinstance(postgres_service, JdbcConnectionService):
            raise ValueError("postgres_service must be an instance of JdbcConnectionService")

        self.alarm_service = alarm_service
        self.email_service = email_service
        self.postgres_service = postgres_service

        if isinstance(distribution_list, str):
            distribution_list = distribution_list.split(',')

        self.validate_parameters(distribution_list, from_addr)
        self.distribution_list = distribution_list
        self.from_addr = from_addr

        self.sql = self.load_sql_files()

    def validate_parameters(self, distribution_list=None, from_addr=None):
        if not distribution_list or not isinstance(distribution_list, list):
            raise ValueError("distribution_list must have at least one entry")

        for email in distribution_list:
            if not self.EMAIL_REGEX.fullmatch(email):
                raise ValueError(f"Invalid email address in distribution_list: {email}")

        if not self.EMAIL_REGEX.fullmatch(from_addr):
            raise ValueError("from_addr must be a valid email address")

    def load_sql_files(self):
        pkg = "dwh.jobs.sql_example"
        sql_file = 'sql_example.sql'
        try:
            return files(pkg).joinpath(sql_file).read_text()
        except Exception as e:
            raise RuntimeError(f"Failed to load SQL from {sql_file}: {e}")

    # tellme: be explicit about parameters and their types. DO NOT USE **ARGS OR **KWARGS
    def execute_job(self, start_date, end_date):
        self.validate_params(start_date, end_date)

        results = self.execute_query(start_date, end_date)

        self.send_email(start_date, results)

        return results

    def validate_params(self, start_date, end_date):
        if not start_date:
            raise ValueError("start_date is required")
        if not end_date:
            raise ValueError("end_date is required")

        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("start_date must be formatted as 'YYYY-MM-DD'")

        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("end_date must be formatted as 'YYYY-MM-DD'")

        if end_dt < start_dt:
            raise ValueError("end_date cannot be before start_date")

    def execute_query(self, start_date, end_date):
        results = self.postgres_service.execute_query(
            sql=self.sql,
            params={
                'start_dt': start_date,
                'end_dt': end_date
            }
        )
        print(f"SQL Query executed successfully for date range: {start_date} to {end_date} with results: {results}")

        return results

    def send_email(self, start_date, results):
        #     todo: send email with results
        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_addr
        msg['bcc'] = ', '.join(self.distribution_list)
        msg['Subject'] = 'Glue Job Success Email: ' + start_date

        body = "hello world!"
        part1 = MIMEText(body, 'html')
        msg.attach(part1)
        self.email_service.send_email(
            msg=msg,
            from_addr=self.from_addr,
            bcc_addr=self.distribution_list
        )

        print(f"Email sent successfully to {', '.join(self.distribution_list)} with subject: {msg['Subject']}")

    def on_success(self, results: str) -> None:
        """
        Send a notification using the notification service.
        """
        class_name = self.__class__.__name__
        subject = f"{class_name}: Job Completed Successfully"
        print(f"{subject} with results: {results}")

    def on_failure(self, error_message) -> None:
        """
        Send a notification using the notification service.
        """
        try:
            class_name = self.__class__.__name__
            subject = f"{class_name}: Job Execution Failed"
            self.alarm_service.send_notification(subject=subject, message=error_message)
        except Exception as e:
            print(f"Exception sending notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e
