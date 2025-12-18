"""
Simple ETL Job Example
======================

A minimal example showing the SparkRouter job pattern.

This job demonstrates:
- Extending AbstractJob
- Implementing execute_job() with explicit parameters
- Handling success and failure notifications
- Dependency injection for testability
"""

from typing import Any

from sparkrouter import AbstractJob, NotificationService


class SimpleETLJob(AbstractJob):
    """
    A simple ETL job that processes data.

    Dependencies are injected via constructor, making the job
    testable without mocks.
    """

    def __init__(
        self,
        notification_service: NotificationService,
    ):
        """
        Initialize the job with dependencies.

        Args:
            notification_service: Service for sending notifications.
        """
        self.notification_service = notification_service

    def execute_job(
        self,
        input_path: str,
        output_path: str,
        filter_column: str = "status",
        filter_value: str = "active",
    ) -> dict:
        """
        Execute the ETL logic.

        Note: Use explicit parameters instead of **kwargs for clarity
        and better IDE support.

        Args:
            input_path: Path to read input data from.
            output_path: Path to write output data to.
            filter_column: Column to filter on.
            filter_value: Value to filter for.

        Returns:
            Dict with job results/metrics.
        """
        print(f"Reading data from: {input_path}")
        print(f"Filtering where {filter_column} = '{filter_value}'")
        print(f"Writing results to: {output_path}")

        # In a real job, you would:
        # df = self.reader.read(input_path)
        # filtered = df.filter(df[filter_column] == filter_value)
        # self.writer.write(filtered, output_path)

        # Return metrics for on_success()
        return {
            "input_path": input_path,
            "output_path": output_path,
            "records_processed": 1000,  # Would be actual count
            "records_written": 850,      # Would be actual count
        }

    def on_success(self, results: Any) -> None:
        """
        Handle successful job completion.

        Args:
            results: The dict returned from execute_job().
        """
        message = (
            f"Successfully processed {results['records_processed']} records.\n"
            f"Wrote {results['records_written']} records to {results['output_path']}"
        )
        self.notification_service.send_notification(
            subject="SimpleETLJob: Success",
            message=message,
        )

    def on_failure(self, error_message: str) -> None:
        """
        Handle job failure.

        Args:
            error_message: Description of what went wrong.
        """
        self.notification_service.send_notification(
            subject="SimpleETLJob: FAILED",
            message=error_message,
        )
