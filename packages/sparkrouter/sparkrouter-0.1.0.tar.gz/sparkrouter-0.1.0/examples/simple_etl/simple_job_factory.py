"""
Simple ETL Job Factory
======================

Factory for creating SimpleETLJob instances with proper dependency injection.

This module demonstrates:
- Extending AbstractJobFactory
- Parsing JSON configuration from CLI args
- Creating jobs with injected dependencies
- The main() entry point pattern
"""

from sparkrouter import AbstractJobFactory
from sparkrouter.testing.noop import NoopNotificationService

from examples.simple_etl.simple_job import SimpleETLJob


class SimpleETLJobFactory(AbstractJobFactory):
    """
    Factory for creating SimpleETLJob instances.

    The factory is responsible for:
    1. Parsing configuration from CLI arguments
    2. Creating service dependencies
    3. Assembling the job with all dependencies injected
    """

    def create_job(self, **kwargs) -> SimpleETLJob:
        """
        Create a SimpleETLJob with dependencies.

        Args:
            **kwargs: Must include 'simple_etl_job' config key.

        Returns:
            Configured SimpleETLJob instance.
        """
        # Parse job-specific configuration
        config = self.parse_job_config(job_name="simple_etl_job", **kwargs)

        # Create notification service based on config
        # In production, you might use SNS, Slack, etc.
        notification_config = config.get("notification", {})
        notification_service = self._create_notification_service(notification_config)

        # Create and return the job with dependencies injected
        return SimpleETLJob(
            notification_service=notification_service,
        )

    def _create_notification_service(self, config: dict):
        """
        Create a notification service based on configuration.

        In a real application, this might return different implementations
        based on the 'type' field in config (SNS, Slack, Email, etc.)
        """
        service_type = config.get("type", "noop")

        if service_type == "noop":
            return NoopNotificationService()
        # Add more notification types as needed:
        # elif service_type == "sns":
        #     return SNSNotificationService(
        #         region=config["region"],
        #         topic_arn=config["topic_arn"],
        #     )
        else:
            raise ValueError(f"Unknown notification service type: {service_type}")


def main(**kwargs):
    """
    Entry point for the job.

    This function is called by the platform entry points (Databricks, Glue, etc.)
    via dynamic import: importlib.import_module(module_name).main(**kwargs)

    Args:
        **kwargs: All CLI arguments passed to the entry point.

    Returns:
        Job execution result.
    """
    factory = SimpleETLJobFactory()
    return factory.run(**kwargs)


# Example CLI invocation:
#
# python -m sparkrouter.entry_points.container \
#     --module_name examples.simple_etl.simple_job_factory \
#     --simple_etl_job '{"notification": {"type": "noop"}}' \
#     --input_path "s3://bucket/input/" \
#     --output_path "s3://bucket/output/"
