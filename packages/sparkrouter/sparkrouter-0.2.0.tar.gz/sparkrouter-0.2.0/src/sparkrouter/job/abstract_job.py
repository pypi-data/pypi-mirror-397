from abc import ABC, abstractmethod
from typing import Any, final


class AbstractJob(ABC):
    """
    Abstract base class for jobs using the Template Method pattern.

    The `run()` method is final and defines the execution flow:
    1. Call `execute_job(**kwargs)` - your business logic
    2. On success: call `on_success(results)`
    3. On failure: call `on_failure(error_message)`, then re-raise

    Subclasses must implement:
    - execute_job(**kwargs): The main business logic
    - on_success(results): Called when job succeeds
    - on_failure(error_message): Called when job fails

    Example:
        class MyETLJob(AbstractJob):
            def __init__(self, reader, writer):
                self.reader = reader
                self.writer = writer

            def execute_job(self, input_path: str, output_path: str) -> dict:
                df = self.reader.read(input_path)
                transformed = df.filter(df.status == "active")
                self.writer.write(transformed, output_path)
                return {"records_written": transformed.count()}

            def on_success(self, results):
                print(f"Success! Wrote {results['records_written']} records")

            def on_failure(self, error_message):
                print(f"Failed: {error_message}")
    """

    @abstractmethod
    def execute_job(self, **kwargs) -> Any:
        """
        Execute the job's business logic.

        This method must be implemented by subclasses. Use explicit parameters
        in your implementation rather than **kwargs for clarity.

        Args:
            **kwargs: Job-specific parameters.

        Returns:
            Any: Results to be passed to on_success().

        Raises:
            Exception: Any exception will trigger on_failure() and be re-raised.
        """
        raise NotImplementedError("Subclasses must implement execute_job()")

    @abstractmethod
    def on_success(self, results: Any) -> None:
        """
        Handle successful job execution.

        Called automatically by run() when execute_job() completes without error.

        Args:
            results: The return value from execute_job().
        """
        raise NotImplementedError("Subclasses must implement on_success()")

    @abstractmethod
    def on_failure(self, error_message: str) -> None:
        """
        Handle job execution failure.

        Called automatically by run() when execute_job() raises an exception.
        The original exception is re-raised after this method completes.

        Args:
            error_message: A formatted error message describing the failure.
        """
        raise NotImplementedError("Subclasses must implement on_failure()")

    @final
    def run(self, **kwargs) -> Any:
        """
        Execute the job with the Template Method pattern.

        This method is final and cannot be overridden. It provides the
        standard execution flow for all jobs:
        1. Call execute_job() with provided kwargs
        2. On success: call on_success() with results
        3. On failure: call on_failure(), then re-raise the exception

        Args:
            **kwargs: Parameters to pass to execute_job().

        Returns:
            Any: The results from execute_job().

        Raises:
            RuntimeError: Wraps any exception from execute_job().
        """
        try:
            results = self.execute_job(**kwargs)
            self.on_success(results)
            return results
        except Exception as e:
            class_name = self.__class__.__name__
            error_message = f"{class_name} execution failed: {e}"
            print(error_message)
            self.on_failure(error_message)
            raise RuntimeError(error_message) from e
