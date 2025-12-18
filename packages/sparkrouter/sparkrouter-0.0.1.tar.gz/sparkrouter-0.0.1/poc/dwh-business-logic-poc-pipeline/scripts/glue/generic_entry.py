"""
Generic Entry Point for Glue Jobs
================================

This script serves as a unified entry point for running Python modules as AWS Glue jobs.
It abstracts away Glue-specific setup, allowing jobs to be written as standard Python
modules that can run both in Glue and non-Glue environments.

How It Works
-----------
1. Parses command line arguments passed by AWS Glue
2. Extracts the required 'module_name' parameter pointing to your job module
3. Filters out reserved Glue parameters (JOB_ID, JOB_RUN_ID)
4. Adds Glue-specific context parameters (spark_service='GLUE')
5. Dynamically imports the specified Python module
6. Calls the module's main() function, passing all parameters as kwargs

MWAA Integration
--------------
When calling from Amazon MWAA (Managed Workflows for Apache Airflow):

1. Create a GlueJobOperator or PythonOperator that calls this script
2. Always include the 'module_name' parameter with the full import path to your job
3. Example DAG task:
    task = GlueJobOperator(
        task_id='process_data',
        job_name='data_processing_job',
        script_location='s3://bucket/scripts/glue/generic_entry.py',
        script_args={
            '--module_name': 'myproject.jobs.data_processor',
            '--input_path': 's3://bucket/input/',
            '--output_path': 's3://bucket/output/'
        }
    )

Parameter Handling
----------------
The main convenience of this approach is that required Glue parameters are automatically set
by simply calling this entry point from a Glue operator. Your DAG doesn't need to worry
about setting up these parameters.
"""
import os
import sys
import importlib
import importlib.util


# Reserved arguments - removed from the job args
RESERVED_ARGS = {'module_name', 'JOB_ID', 'JOB_RUN_ID'}


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
    Prepare arguments for module execution by removing reserved args and adding execution context.

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

    # Add execution context
    cleaned_args['service_provider'] = 'GLUE'

    # Add environment and region from environment variables if not already provided
    if 'environment' not in cleaned_args:
        cleaned_args['environment'] = os.environ.get('ENVIRONMENT', None)
    if 'region' not in cleaned_args:
        cleaned_args['region'] = os.environ.get('AWS_REGION', os.environ.get('AWS_DEFAULT_REGION', None))

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

    # Check for Glue-specific environment variable
    if os.environ.get("GLUE_COMMAND_CRITERIA", "").lower() == "glueetl":
        return True

    # Check PYTHONPATH for pyspark
    pythonpath = os.environ.get("PYTHONPATH", "")
    for path in pythonpath.split(os.pathsep):
        if "pyspark" in path.lower():
            return True

    #  last ditch attempt - doesn't seem to work
    pyspark_spec = importlib.util.find_spec("pyspark")
    if pyspark_spec is not None:
        try:
            from pyspark import SparkContext
            return SparkContext._active_spark_context is not None
        except ImportError:
            return False
    return False



def print_env_variables():
    print("environment variables:")
    for key, value in os.environ.items():
        print(f"{key}: {value}")



def main(argv=None):
    """
    Main entry point for the script.

    Args:
        argv: Command line arguments (defaults to sys.argv if None)
    """
    if argv is None:
        argv = sys.argv
    
    print("Starting Glue job...")
    print("sys args:", argv)
    print_env_variables()

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