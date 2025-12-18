from abc import ABC, abstractmethod
from typing import final, Any


class AbstractJob(ABC):
    """
    Abstract base class for jobs.

    Most basic assumption is that a job will execute some logic and send notifications.
    This class can be extended with other abstract classes to provide additional capabilities.

    Subclasses must implement:
    - execute_job(**kwargs): The main business logic
    - on_success(results): Called when job succeeds
    - on_failure(error_message): Called when job fails
    """

    @abstractmethod
    def execute_job(self, **kwargs) -> Any:
        """
        Abstract method to execute job business logic. Must be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def on_success(self, results: Any) -> None:
        """
        Method to handle successful job execution.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @abstractmethod
    def on_failure(self, error_message: str) -> None:
        """
        Method to handle job execution failure.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    @final
    def run(self, **kwargs):
        """
        This is the main entry point for running the job.
        :param kwargs:
        :return:
        """
        try:
            results = self.execute_job(**kwargs)

            self.on_success(results)
        except Exception as e:
            class_name = self.__class__.__name__
            error_message = f"Job execution failed: {str(e)}"
            print(f"{class_name}: {error_message}")
            self.on_failure(error_message)
            raise RuntimeError(error_message) from e
