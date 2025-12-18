from dwh.jobs.abstract_job import AbstractJob
from dwh.services.notification.notification_service import NotificationService


class SparkExampleJob(AbstractJob):

    #  tellme:
    #   always be explicit about required parameters and services.
    #   do not use **kwargs in concrete implementations
    def __init__(self,
                 alarm_service: NotificationService,
                 success_service: NotificationService,
                 spark_session):
        super(SparkExampleJob, self).__init__()

        if not isinstance(alarm_service, NotificationService):
            raise ValueError("alarm_service must be an instance of NotificationService")

        if not isinstance(success_service, NotificationService):
            raise ValueError("success_service must be an instance of NotificationService")

        if not spark_session:
            raise ValueError("spark_session is required and must be a valid Spark session")

        self.alarm_service = alarm_service
        self.success_service = success_service
        self.spark_session = spark_session

    #  tellme:
    #   always be explicit about required parameters.
    #   do not use **kwargs in concrete implementations
    #   services should be provided as part of class instantiation
    def execute_job(self, example: str):
        if not isinstance(example, str):
            raise ValueError("example must be a string")

        print("Hello from spark!")
        print("example value is :", example)

        df = self.spark_session.createDataFrame([{"example": example}])
        df.show()

        success_message = "Job executed successfully"

        return success_message

    def on_success(self, results: str) -> None:
        """
        Send a notification using the notification service.
        """
        try:
            class_name = self.__class__.__name__
            subject = f"{class_name}: Job Completed Successfully"
            self.success_service.send_notification(subject=subject, message=results)
        except Exception as e:
            print(f"Exception sending success notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e

    def on_failure(self, error_message) -> None:
        """
        Send a notification using the notification service.
        """
        try:
            class_name = self.__class__.__name__
            subject = f"{class_name}: Job Execution Failed"
            self.alarm_service.send_notification(subject=subject, message=error_message)
        except Exception as e:
            print(f"Exception sending alarm notification: {e}")
            raise RuntimeError(f"Failed to send notification: {e}") from e
