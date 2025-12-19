import inspect
import json
from abc import ABC, abstractmethod
from typing import Any, Dict

from sparkrouter.job.abstract_job import AbstractJob


class AbstractJobFactory(ABC):
    """
    Abstract factory for creating and running job instances.

    This class provides:
    - JSON configuration parsing from CLI arguments
    - Job creation via the factory method pattern
    - Job execution with automatic parameter filtering

    The factory pattern allows jobs to be created with their dependencies
    injected, making them testable without mocks.

    Subclasses must implement:
    - create_job(**kwargs): Create a job instance with dependencies

    Example:
        class MyETLJobFactory(AbstractJobFactory):
            def create_job(self, **kwargs) -> MyETLJob:
                config = self.parse_job_config(job_name='my_etl_job', **kwargs)
                spark = SparkSession.builder.getOrCreate()
                return MyETLJob(
                    reader=ParquetReader(spark),
                    writer=ParquetWriter(spark),
                )

        def main(**kwargs):
            factory = MyETLJobFactory()
            return factory.run(**kwargs)
    """

    def __init__(self, **kwargs):
        """
        Initialize the factory.

        Args:
            **kwargs: Additional arguments for future extensibility.
        """
        pass

    def parse_job_config(self, job_name: str, **kwargs) -> Dict[str, Any]:
        """
        Parse job configuration from kwargs.

        Handles both dict and JSON string formats for configuration,
        which is useful when configs are passed via CLI arguments.

        Args:
            job_name: The key to look up in kwargs for the job's config.
            **kwargs: All arguments passed to the factory.

        Returns:
            Dict[str, Any]: The parsed configuration dictionary.

        Raises:
            ValueError: If job_name is missing, config is missing,
                       or JSON parsing fails.

        Example:
            # From CLI: --my_job '{"input": "s3://bucket/path"}'
            config = self.parse_job_config(job_name='my_job', **kwargs)
            # config == {"input": "s3://bucket/path"}
        """
        if not job_name:
            raise ValueError("job_name is required")

        config = kwargs.get(job_name)
        if config is None:
            raise ValueError(f"Configuration for '{job_name}' is required")

        if isinstance(config, str):
            try:
                config = json.loads(config)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON format for '{job_name}': {config}"
                ) from e
        elif not isinstance(config, dict):
            raise ValueError(
                f"'{job_name}' must be a dict or JSON string, got {type(config).__name__}"
            )

        return config

    @abstractmethod
    def create_job(self, **kwargs) -> AbstractJob:
        """
        Create a job instance with dependencies injected.

        This method must be implemented by subclasses to create the specific
        job type with all required dependencies.

        Args:
            **kwargs: Configuration parameters for the job.

        Returns:
            AbstractJob: A configured job instance ready to run.

        Example:
            def create_job(self, **kwargs) -> MyETLJob:
                config = self.parse_job_config(job_name='my_etl_job', **kwargs)
                return MyETLJob(
                    reader=self.create_reader(config),
                    writer=self.create_writer(config),
                )
        """
        raise NotImplementedError("Subclasses must implement create_job()")

    def run(self, **kwargs) -> Any:
        """
        Create and run a job with automatic parameter filtering.

        This method:
        1. Creates a job instance via create_job()
        2. Inspects the job's execute_job() signature
        3. Filters kwargs to only include valid parameters
        4. Calls job.run() with the filtered parameters

        Args:
            **kwargs: Parameters for job creation and execution.

        Returns:
            Any: The result from job execution.
        """
        job = self.create_job(**kwargs)

        # Get the signature of execute_job to filter kwargs
        sig = inspect.signature(job.execute_job)

        # Only pass parameters that exist in the method signature
        valid_params = {k: v for k, v in kwargs.items() if k in sig.parameters}

        return job.run(**valid_params)
