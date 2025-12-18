"""
Base Entry Point Module
=======================

Common parsing and execution logic shared by all platform entry points.

This module provides the foundation for platform-specific entry points,
handling argument parsing, module loading, and execution.
"""

import importlib
import sys
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple


def parse_args(argv: List[str]) -> Dict[str, any]:
    """
    Parse command line arguments into a dictionary.

    Handles --key value pairs and --flag (boolean) arguments.

    Args:
        argv: List of command line arguments (typically sys.argv).

    Returns:
        Dict with parsed arguments as key-value pairs.

    Example:
        >>> parse_args(['script.py', '--module_name', 'my.module', '--verbose'])
        {'module_name': 'my.module', 'verbose': True}
    """
    args = {}
    key = None
    for arg in argv[1:]:  # Skip script name
        if arg.startswith('--'):
            key = arg[2:]
            args[key] = True  # Default to True for flags
        elif key:
            args[key] = arg
            key = None
    return args


def validate_required_args(args: Dict[str, any], required: List[str]) -> None:
    """
    Validate that required arguments are present.

    Args:
        args: Dictionary of parsed arguments.
        required: List of required argument names.

    Raises:
        RuntimeError: If any required arguments are missing.
    """
    missing = [arg for arg in required if arg not in args]
    if missing:
        raise RuntimeError(f"Missing required argument(s): {', '.join(missing)}")


def execute_module(module_name: str, module_args: Dict[str, any]) -> any:
    """
    Import and execute a module's main() function.

    Args:
        module_name: Fully qualified module name to import.
        module_args: Arguments to pass to the module's main() function.

    Returns:
        The return value from the module's main() function.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the module has no main() function.
    """
    job_module = importlib.import_module(module_name)
    return job_module.main(**module_args)


class BaseEntryPoint(ABC):
    """
    Abstract base class for platform-specific entry points.

    Subclasses implement platform-specific argument preparation
    while sharing common parsing and execution logic.

    Example:
        class MyPlatformEntryPoint(BaseEntryPoint):
            @property
            def service_provider(self) -> str:
                return "MY_PLATFORM"

            @property
            def reserved_args(self) -> set:
                return {'module_name', 'platform_specific_arg'}

            def add_platform_context(self, args: Dict) -> Dict:
                args['platform_feature'] = self.detect_feature()
                return args
    """

    @property
    @abstractmethod
    def service_provider(self) -> str:
        """Return the service provider identifier (e.g., 'DATABRICKS', 'GLUE')."""
        raise NotImplementedError

    @property
    def reserved_args(self) -> set:
        """
        Return set of reserved argument names to exclude from job args.

        Override to add platform-specific reserved arguments.
        """
        return {'module_name'}

    def add_platform_context(self, args: Dict[str, any]) -> Dict[str, any]:
        """
        Add platform-specific context to arguments.

        Override to add environment variables, platform detection, etc.

        Args:
            args: The current argument dictionary.

        Returns:
            Updated argument dictionary with platform context.
        """
        return args

    def detect_spark(self) -> bool:
        """
        Detect if Spark is available in the current environment.

        Override for platform-specific Spark detection.

        Returns:
            True if Spark is available, False otherwise.
        """
        try:
            import importlib.util
            return importlib.util.find_spec("pyspark") is not None
        except ImportError:
            return False

    def prepare_module_args(self, args: Dict[str, any]) -> Tuple[str, Dict[str, any]]:
        """
        Prepare arguments for module execution.

        Removes reserved args, adds service provider, and applies
        platform-specific context.

        Args:
            args: Dictionary of parsed arguments.

        Returns:
            Tuple of (module_name, cleaned_args).
        """
        cleaned_args = args.copy()

        # Extract module name
        module_name = cleaned_args.pop('module_name')

        # Remove reserved args
        for reserved in self.reserved_args:
            cleaned_args.pop(reserved, None)

        # Add service provider
        cleaned_args['service_provider'] = self.service_provider

        # Add Spark detection
        if self.detect_spark():
            cleaned_args['has_spark'] = True

        # Add platform-specific context
        cleaned_args = self.add_platform_context(cleaned_args)

        return module_name, cleaned_args

    def run(self, argv: Optional[List[str]] = None) -> any:
        """
        Main entry point execution.

        Args:
            argv: Command line arguments (defaults to sys.argv).

        Returns:
            The result from module execution.

        Raises:
            RuntimeError: If required arguments are missing.
            ImportError: If the module cannot be imported.
        """
        if argv is None:
            argv = sys.argv

        print(f"Starting {self.service_provider} job...")
        print(f"Arguments: {argv}")

        try:
            args = parse_args(argv)
            validate_required_args(args, ['module_name'])

            module_name, module_args = self.prepare_module_args(args)
            print(f"Running module: {module_name}")
            print(f"Module args: {module_args}")

            return execute_module(module_name, module_args)

        except Exception as e:
            print(f"Error running job: {e}")
            raise
