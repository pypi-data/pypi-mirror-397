from datetime import datetime
from dwh.jobs.abstract_job import AbstractJob
from dwh.services.notification.notification_service import NotificationService


class GenericExampleJob(AbstractJob):

    def __init__(self, alarm_service: NotificationService):
        if not isinstance(alarm_service, NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        self.alarm_service = alarm_service

    #  tellme: be explicit about required parameters. DO NOT USE **KWARGS here
    def execute_job(self, start_date, end_date) -> str:

        self.validate_params(start_date, end_date)

        results = "Job executed successfully with start_date: {}, end_date: {}".format(start_date, end_date)

        print("Hello from generic example!")
        print("start_date :", start_date)
        print("end_date :", end_date)

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
