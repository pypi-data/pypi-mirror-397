import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any

from dwh.jobs.abstract_job import AbstractJob


class AbstractJobFactory(ABC):
    """
    Abstract factory for creating job instances.
    
    This class provides a common interface for job factories and handles
    parameter parsing and job execution.
    """
    def __init__(self, **kwargs):
        #  we capture kwargs for future proofing
        pass

    def parse_job_config(self, job_name: str, **kwargs) -> Dict[str, Any]:
        """Parse job configuration from kwargs."""
        if not job_name:
            raise ValueError("job_name is required")

        config = kwargs.get(job_name)
        if isinstance(config, str):
            # If it's a string, try to parse it as JSON
            import json
            try:
                config = json.loads(config)
            except json.JSONDecodeError:
                raise ValueError(
                    f"Invalid JSON format for {job_name}_notification_service: {config}")
        elif not isinstance(config, dict):
            raise ValueError(
                f"{job_name} value must be a dict or a JSON string, got {type(config)}")

        return config

    @abstractmethod
    def create_job(self, **kwargs) -> AbstractJob:
        """
        Create a job instance with the specified configuration.
        
        This method must be implemented by subclasses to create the specific job type.
        
        Args:
            **kwargs: Configuration parameters for the job.
            
        Returns:
            An instance of AbstractJob.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def run(self, **kwargs):
        """
        Create and run a job with the specified parameters.
        
        This method creates a job instance and executes it with the provided parameters.
        
        Args:
            **kwargs: Parameters for job creation and execution.
            
        Returns:
            The result of job execution.
        """
        # Create the job
        job = self.create_job(**kwargs)
        
        # Debug log original kwargs
        print(f"Original kwargs: {kwargs}")

        # Get the signature of the execute_job method
        sig = inspect.signature(job.execute_job)

        # Filter kwargs to only include parameters that exist in the method signature
        valid_params = {k: v for k, v in kwargs.items() if k in sig.parameters}

        # Debug log the filtered kwargs
        print(f"Filtered kwargs: {valid_params}")

        # Run the job
        return job.run(**valid_params)
