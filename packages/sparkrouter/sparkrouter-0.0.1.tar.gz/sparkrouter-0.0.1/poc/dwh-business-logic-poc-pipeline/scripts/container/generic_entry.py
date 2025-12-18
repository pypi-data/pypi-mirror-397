#!/usr/bin/env python
"""
Generic Entry Point for Spark Jobs
=================================

This script serves as a unified entry point for running Python modules as Spark jobs.
It abstracts away Spark-specific setup, allowing jobs to be written as standard Python
modules that can run in different environments.
"""

import sys
import importlib
import importlib.util

# Reserved arguments - removed from the job args
RESERVED_ARGS = {'module_name'}


def parse_args(argv):
    """
    Parse command line arguments into a dictionary.

    Args:
        argv: List of command line arguments (typically sys.argv)

    Returns:
        dict: Parsed arguments as key-value pairs
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


def validate_required_args(args):
    """
    Validate that required arguments are present.
    
    Args:
        args: Dictionary of parsed arguments
    
    Raises:
        RuntimeError: If required arguments are missing
    """
    if 'module_name' not in args:
        raise RuntimeError("Missing required argument: module_name")


def prepare_module_args(args):
    """
    Prepare arguments for module execution by removing reserved args and adding service provider.
    
    Args:
        args: Dictionary of parsed arguments
    
    Returns:
        tuple: (module_name, cleaned_args_dict)
    """
    # Make a copy to avoid modifying original
    cleaned_args = args.copy()
    
    # Extract module name
    module_name = cleaned_args.pop('module_name')
    
    # Remove other reserved args
    for reserved in RESERVED_ARGS:
        cleaned_args.pop(reserved, None)
    
    # Add service provider
    cleaned_args['service_provider'] = 'CONTAINER'
    
    return module_name, cleaned_args


def execute_module(module_name, module_args):
    """
    Import and execute the specified module.
    
    Args:
        module_name: Name of module to import and execute
        module_args: Dictionary of arguments to pass to module's main() function
    
    Raises:
        ImportError: If module cannot be imported
        Exception: If module execution fails
    """
    job_module = importlib.import_module(module_name)
    job_module.main(**module_args)


def is_spark_job():
    """
    Check if the current environment is a Spark job.

    Returns:
        bool: True if running in a Spark job, False otherwise
    """
    pyspark_spec = importlib.util.find_spec("pyspark")
    if pyspark_spec is not None:
        print("pyspark_spec is not None, running in Spark environment")
        has_spark = True
    else:
        print("pyspark_spec is None, not running in Spark environment")
        has_spark = False

    return has_spark


def main(argv=None):
    """
    Main entry point for the script.
    
    Args:
        argv: Command line arguments (defaults to sys.argv if None)
    """
    if argv is None:
        argv = sys.argv
    
    print("Starting Spark job...")
    print("sys args:", argv)
    
    try:
        # Parse and validate arguments
        args = parse_args(argv)
        validate_required_args(args)
        
        # Prepare module execution
        module_name, module_args = prepare_module_args(args)
        if is_spark_job():
            # If running in Spark, add Spark session to module args
            print("Detected Spark job, adding has_spark variable to module args")
            module_args['has_spark'] = True

        print(f"Running job module: {module_name} with args: {module_args}")
        
        # Execute the module
        execute_module(module_name, module_args)
        
    except Exception as e:
        print(f"Error running job: {str(e)}")
        raise


if __name__ == "__main__":
    main()