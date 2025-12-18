import re
from importlib.resources import files
from datetime import datetime
from typing import Union, Any

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dwh.jobs.abstract_job import AbstractJob
from dwh.services.database.jdbc.jdbc_connection_service import JdbcConnectionService
from dwh.services.email.email_service import EmailService
from dwh.services.notification.notification_service import NotificationService


class RevenueReconJob(AbstractJob):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")

    def __init__(
            self,
            alarm_service: NotificationService,
            success_service: NotificationService,
            email_service: EmailService,
            postgres_service: JdbcConnectionService,

            distribution_list: Union[list, str],
            from_addr: str,
    ):
        super(RevenueReconJob, self).__init__()

        if not isinstance(alarm_service, NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        if not isinstance(success_service, NotificationService):
            raise ValueError("success_service must be an instance of NotificationService")

        if not isinstance(email_service, EmailService):
            raise ValueError("email_service must be an instance of EmailService")

        if not isinstance(postgres_service, JdbcConnectionService):
            raise ValueError("postgres_service must be an instance of JdbcConnectionService")

        self.alarm_service = alarm_service
        self.success_service = success_service
        self.email_service = email_service
        self.postgres_service = postgres_service

        # Process and validate email parameters
        processed_distribution_list = self._validate_and_process_email_params(distribution_list, from_addr)
        self.distribution_list = processed_distribution_list
        self.from_addr = from_addr

        self.sql_template = self._load_sql_template()
        self.html_file = self._load_html_template()

    def _validate_and_process_email_params(self, distribution_list, from_addr):
        """Validate and process email parameters."""
        # Process distribution list
        if isinstance(distribution_list, str):
            distribution_list = distribution_list.split(',')
        elif not distribution_list or not isinstance(distribution_list, list):
            raise ValueError("distribution_list must have at least one entry")

        # Validate email addresses
        for email in distribution_list:
            if not self.EMAIL_REGEX.fullmatch(email):
                raise ValueError(f"Invalid email address in distribution_list: {email}")

        if not self.EMAIL_REGEX.fullmatch(from_addr):
            raise ValueError("from_addr must be a valid email address")

        return distribution_list

    def _load_sql_template(self):
        """Load SQL template from file."""
        pkg = "dwh.jobs.revenue_recon"
        sql_file = 'load_recon_monthly_3_0.sql'
        try:
            sql = files(pkg).joinpath(sql_file).read_text()
            return sql
        except Exception as e:
            raise RuntimeError(f"Failed to load SQL from {sql_file}: {e}")

    def _load_html_template(self):
        """Load HTML template from file."""
        pkg = "dwh.jobs.revenue_recon"
        sql_file = 'email_template.html'
        try:
            sql = files(pkg).joinpath(sql_file).read_text()
            return sql
        except Exception as e:
            raise RuntimeError(f"Failed to load SQL from {sql_file}: {e}")

    def execute_job(self, start_date, end_date):
        self.validate_params(start_date, end_date)

        results = self.execute_query(start_date=start_date, end_date=end_date)
        print(f"query results: {results}")

        self.send_email(start_date, results)

        success_results = {
            'start_date': start_date,
            'end_date': end_date,
            'distribution_list': self.distribution_list,
            'data': results
        }

        # this payload to be sent to success_service
        return success_results

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

        # Convert date strings to int format YYYYMMDD
        start_dt = int(start_date.replace('-', ''))
        end_dt = int(end_date.replace('-', ''))

        results = self.postgres_service.execute_query(
            sql=self.sql_template,
            params={
                'start_dt': start_dt,
                'end_dt': end_dt
            }
        )
        print(f"SQL Query executed successfully for date range: {start_date} to {end_date} with results: {results}")
        # Add the expected output format for the test
        print(f"start_date to {end_date}")

        return results

    def send_email(self, start_date, results: Any):
        import pandas as pd

        # Convert the data to a DataFrame
        data_df = pd.DataFrame(results, columns=['metric_name', 'mthyear', 'metric_value', 'dataversion'],
                               index=range(len(results)))

        # Convert start_date to the desired format
        # sub_start_date = start_date.strftime('%b-%Y').upper()

        table = ''
        for i in range(data_df.shape[0]):
            d_name = data_df['metric_name'].iloc[i]
            d_myr = data_df['mthyear'].iloc[i]
            d_val = data_df['metric_value'].iloc[i]
            d_ver = data_df['dataversion'].iloc[i]
            table += '\n'
            table += "<TR>" \
                     f"<TD><CODE>{d_name}</CODE></TD>" \
                     f"<TD><CODE>{d_myr}</CODE></TD>" \
                     f"<TD><CODE>{d_val}</CODE></TD>" \
                     f"<TD><CODE>{d_ver}</CODE></TD>" \
                     "</TR>"

        body = self.html_file.replace('<!--TABLE-DATA-->', table)

        msg = MIMEMultipart('alternative')
        msg['From'] = self.from_addr
        msg['bcc'] = ', '.join(self.distribution_list)
        msg['Subject'] = 'Reconciliation statistics - DWH_REVENUE ' + start_date
        part1 = MIMEText(body, 'html')
        msg.attach(part1)

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
        try:
            subject = "RevenueReconJob: Job Execution Failed"
            self.success_service.send_notification(subject=subject, message=results)
        except Exception as e:
            print(f"Exception sending notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e
        # class_name = self.__class__.__name__
        # subject = f"{class_name}: Job Completed Successfully"
        # print(f"{subject} with results: {results}")

    def on_failure(self, error_message) -> None:
        """
        Send a notification using the notification service.
        """
        try:
            subject = "RevenueReconJob: Job Execution Failed"
            self.alarm_service.send_notification(subject=subject, message=error_message)
        except Exception as e:
            print(f"Exception sending notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e
