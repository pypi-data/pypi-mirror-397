"""Tests for entry point parsing and base functionality."""

import pytest

from sparkrouter.entry_points.base import (
    parse_args,
    validate_required_args,
    BaseEntryPoint,
)
from sparkrouter.entry_points.databricks import DatabricksEntryPoint
from sparkrouter.entry_points.glue import GlueEntryPoint
from sparkrouter.entry_points.container import ContainerEntryPoint


class TestParseArgs:
    """Tests for argument parsing."""

    def test_parse_key_value_pairs(self):
        argv = ["script.py", "--module_name", "my.module", "--input", "path/to/input"]
        result = parse_args(argv)
        assert result == {
            "module_name": "my.module",
            "input": "path/to/input"
        }

    def test_parse_boolean_flags(self):
        argv = ["script.py", "--verbose", "--debug"]
        result = parse_args(argv)
        assert result == {"verbose": True, "debug": True}

    def test_parse_mixed_args(self):
        argv = ["script.py", "--module_name", "my.module", "--verbose", "--count", "5"]
        result = parse_args(argv)
        assert result == {
            "module_name": "my.module",
            "verbose": True,
            "count": "5"
        }

    def test_parse_json_value(self):
        argv = ["script.py", "--config", '{"key": "value"}']
        result = parse_args(argv)
        assert result == {"config": '{"key": "value"}'}

    def test_parse_empty_args(self):
        argv = ["script.py"]
        result = parse_args(argv)
        assert result == {}

    def test_skips_script_name(self):
        argv = ["my_script.py", "--arg", "value"]
        result = parse_args(argv)
        assert "my_script.py" not in result
        assert result == {"arg": "value"}


class TestValidateRequiredArgs:
    """Tests for required argument validation."""

    def test_passes_when_required_present(self):
        args = {"module_name": "my.module", "other": "value"}
        validate_required_args(args, ["module_name"])  # Should not raise

    def test_raises_when_required_missing(self):
        args = {"other": "value"}
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_args(args, ["module_name"])
        assert "module_name" in str(exc_info.value)

    def test_raises_with_all_missing_args(self):
        args = {}
        with pytest.raises(RuntimeError) as exc_info:
            validate_required_args(args, ["arg1", "arg2"])
        assert "arg1" in str(exc_info.value)
        assert "arg2" in str(exc_info.value)


class TestDatabricksEntryPoint:
    """Tests for Databricks entry point."""

    def test_service_provider(self):
        entry = DatabricksEntryPoint()
        assert entry.service_provider == "DATABRICKS"

    def test_detect_spark_always_true(self):
        entry = DatabricksEntryPoint()
        assert entry.detect_spark() is True

    def test_prepare_module_args_adds_service_provider(self):
        entry = DatabricksEntryPoint()
        args = {"module_name": "my.module", "param": "value"}
        module_name, cleaned = entry.prepare_module_args(args)
        assert module_name == "my.module"
        assert cleaned["service_provider"] == "DATABRICKS"
        assert cleaned["has_spark"] is True
        assert "module_name" not in cleaned


class TestGlueEntryPoint:
    """Tests for Glue entry point."""

    def test_service_provider(self):
        entry = GlueEntryPoint()
        assert entry.service_provider == "GLUE"

    def test_reserved_args_includes_glue_specific(self):
        entry = GlueEntryPoint()
        assert "JOB_ID" in entry.reserved_args
        assert "JOB_RUN_ID" in entry.reserved_args
        assert "JOB_NAME" in entry.reserved_args

    def test_prepare_module_args_removes_glue_reserved(self):
        entry = GlueEntryPoint()
        args = {
            "module_name": "my.module",
            "JOB_ID": "123",
            "JOB_RUN_ID": "456",
            "param": "value"
        }
        module_name, cleaned = entry.prepare_module_args(args)
        assert "JOB_ID" not in cleaned
        assert "JOB_RUN_ID" not in cleaned
        assert cleaned["param"] == "value"


class TestContainerEntryPoint:
    """Tests for Container entry point."""

    def test_service_provider(self):
        entry = ContainerEntryPoint()
        assert entry.service_provider == "CONTAINER"

    def test_prepare_module_args_adds_service_provider(self):
        entry = ContainerEntryPoint()
        args = {"module_name": "my.module"}
        module_name, cleaned = entry.prepare_module_args(args)
        assert cleaned["service_provider"] == "CONTAINER"


class TestCustomEntryPoint:
    """Tests demonstrating how users can create custom entry points."""

    def test_custom_entry_point_subclass(self):
        """Users can subclass ContainerEntryPoint for custom platforms."""
        import os

        class MyCustomEntryPoint(ContainerEntryPoint):
            @property
            def service_provider(self) -> str:
                return "MY_PLATFORM"

            def add_platform_context(self, args):
                args = super().add_platform_context(args)
                args['custom_value'] = 'injected'
                return args

            def detect_spark(self) -> bool:
                return True

        entry = MyCustomEntryPoint()
        assert entry.service_provider == "MY_PLATFORM"
        assert entry.detect_spark() is True

        args = {"module_name": "my.module", "param": "value"}
        module_name, cleaned = entry.prepare_module_args(args)
        assert cleaned["service_provider"] == "MY_PLATFORM"
        assert cleaned["custom_value"] == "injected"
        assert cleaned["has_spark"] is True
