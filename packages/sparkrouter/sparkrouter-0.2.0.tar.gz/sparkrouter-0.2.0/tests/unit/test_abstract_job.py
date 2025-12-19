"""Tests for AbstractJob template method pattern."""

import pytest
from typing import Any

from sparkrouter import AbstractJob


class SuccessfulJob(AbstractJob):
    """Test job that succeeds."""

    def __init__(self):
        self.execute_called = False
        self.success_called = False
        self.failure_called = False
        self.received_results = None

    def execute_job(self, value: int) -> dict:
        self.execute_called = True
        return {"value": value * 2}

    def on_success(self, results: Any) -> None:
        self.success_called = True
        self.received_results = results

    def on_failure(self, error_message: str) -> None:
        self.failure_called = True


class FailingJob(AbstractJob):
    """Test job that fails during execute_job."""

    def __init__(self):
        self.execute_called = False
        self.success_called = False
        self.failure_called = False
        self.received_error = None

    def execute_job(self, **kwargs) -> Any:
        self.execute_called = True
        raise ValueError("Intentional failure")

    def on_success(self, results: Any) -> None:
        self.success_called = True

    def on_failure(self, error_message: str) -> None:
        self.failure_called = True
        self.received_error = error_message


class TestAbstractJobSuccess:
    """Tests for successful job execution."""

    def test_run_calls_execute_job(self):
        job = SuccessfulJob()
        job.run(value=5)
        assert job.execute_called is True

    def test_run_calls_on_success_after_execute(self):
        job = SuccessfulJob()
        job.run(value=5)
        assert job.success_called is True

    def test_run_passes_results_to_on_success(self):
        job = SuccessfulJob()
        job.run(value=5)
        assert job.received_results == {"value": 10}

    def test_run_does_not_call_on_failure(self):
        job = SuccessfulJob()
        job.run(value=5)
        assert job.failure_called is False

    def test_run_returns_results(self):
        job = SuccessfulJob()
        result = job.run(value=5)
        assert result == {"value": 10}


class TestAbstractJobFailure:
    """Tests for failed job execution."""

    def test_run_calls_execute_job(self):
        job = FailingJob()
        with pytest.raises(RuntimeError):
            job.run()
        assert job.execute_called is True

    def test_run_calls_on_failure_when_execute_raises(self):
        job = FailingJob()
        with pytest.raises(RuntimeError):
            job.run()
        assert job.failure_called is True

    def test_run_does_not_call_on_success_when_execute_raises(self):
        job = FailingJob()
        with pytest.raises(RuntimeError):
            job.run()
        assert job.success_called is False

    def test_run_raises_runtime_error_wrapping_original(self):
        job = FailingJob()
        with pytest.raises(RuntimeError) as exc_info:
            job.run()
        assert "FailingJob execution failed" in str(exc_info.value)
        assert "Intentional failure" in str(exc_info.value)

    def test_on_failure_receives_error_message(self):
        job = FailingJob()
        with pytest.raises(RuntimeError):
            job.run()
        assert "Intentional failure" in job.received_error


class TestAbstractJobInterface:
    """Tests for AbstractJob interface requirements."""

    def test_cannot_instantiate_abstract_job_directly(self):
        with pytest.raises(TypeError):
            AbstractJob()

    def test_must_implement_execute_job(self):
        class IncompleteJob(AbstractJob):
            def on_success(self, results):
                pass

            def on_failure(self, error_message):
                pass

        with pytest.raises(TypeError):
            IncompleteJob()

    def test_must_implement_on_success(self):
        class IncompleteJob(AbstractJob):
            def execute_job(self, **kwargs):
                return {}

            def on_failure(self, error_message):
                pass

        with pytest.raises(TypeError):
            IncompleteJob()

    def test_must_implement_on_failure(self):
        class IncompleteJob(AbstractJob):
            def execute_job(self, **kwargs):
                return {}

            def on_success(self, results):
                pass

        with pytest.raises(TypeError):
            IncompleteJob()
