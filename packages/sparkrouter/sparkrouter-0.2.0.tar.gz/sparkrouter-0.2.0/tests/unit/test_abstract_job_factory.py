"""Tests for AbstractJobFactory."""

import pytest
from typing import Any

from sparkrouter import AbstractJob, AbstractJobFactory


class SimpleJob(AbstractJob):
    """Simple test job for factory tests."""

    def __init__(self, multiplier: int = 1):
        self.multiplier = multiplier

    def execute_job(self, value: int) -> dict:
        return {"result": value * self.multiplier}

    def on_success(self, results: Any) -> None:
        pass

    def on_failure(self, error_message: str) -> None:
        pass


class SimpleJobFactory(AbstractJobFactory):
    """Simple test factory."""

    def create_job(self, **kwargs) -> SimpleJob:
        config = self.parse_job_config(job_name="simple_job", **kwargs)
        multiplier = config.get("multiplier", 1)
        return SimpleJob(multiplier=multiplier)


class TestParseJobConfig:
    """Tests for parse_job_config method."""

    def test_parse_dict_config(self):
        factory = SimpleJobFactory()
        config = factory.parse_job_config(
            job_name="my_job",
            my_job={"key": "value"}
        )
        assert config == {"key": "value"}

    def test_parse_json_string_config(self):
        factory = SimpleJobFactory()
        config = factory.parse_job_config(
            job_name="my_job",
            my_job='{"key": "value", "number": 42}'
        )
        assert config == {"key": "value", "number": 42}

    def test_raises_on_missing_job_name(self):
        factory = SimpleJobFactory()
        with pytest.raises(ValueError) as exc_info:
            factory.parse_job_config(job_name="", my_job={})
        assert "job_name is required" in str(exc_info.value)

    def test_raises_on_missing_config(self):
        factory = SimpleJobFactory()
        with pytest.raises(ValueError) as exc_info:
            factory.parse_job_config(job_name="my_job", other_job={})
        assert "Configuration for 'my_job' is required" in str(exc_info.value)

    def test_raises_on_invalid_json(self):
        factory = SimpleJobFactory()
        with pytest.raises(ValueError) as exc_info:
            factory.parse_job_config(job_name="my_job", my_job="not valid json")
        assert "Invalid JSON format" in str(exc_info.value)

    def test_raises_on_non_dict_non_string(self):
        factory = SimpleJobFactory()
        with pytest.raises(ValueError) as exc_info:
            factory.parse_job_config(job_name="my_job", my_job=123)
        assert "must be a dict or JSON string" in str(exc_info.value)


class TestFactoryRun:
    """Tests for factory run method."""

    def test_run_creates_and_executes_job(self):
        factory = SimpleJobFactory()
        result = factory.run(
            simple_job={"multiplier": 3},
            value=5
        )
        assert result == {"result": 15}

    def test_run_filters_kwargs_to_execute_job_signature(self):
        factory = SimpleJobFactory()
        # extra_param should be filtered out since SimpleJob.execute_job
        # only accepts 'value'
        result = factory.run(
            simple_job={"multiplier": 2},
            value=10,
            extra_param="should be ignored"
        )
        assert result == {"result": 20}

    def test_run_with_json_config(self):
        factory = SimpleJobFactory()
        result = factory.run(
            simple_job='{"multiplier": 4}',
            value=3
        )
        assert result == {"result": 12}


class TestFactoryInterface:
    """Tests for AbstractJobFactory interface requirements."""

    def test_cannot_instantiate_abstract_factory_directly(self):
        with pytest.raises(TypeError):
            AbstractJobFactory()

    def test_must_implement_create_job(self):
        class IncompleteFactory(AbstractJobFactory):
            pass

        with pytest.raises(TypeError):
            IncompleteFactory()
