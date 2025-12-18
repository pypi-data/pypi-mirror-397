"""
Custom implementation for creating and running AWS Glue PyShell jobs.

This module provides a workaround for issues with the Airflow GlueJobOperator
when creating and running PyShell jobs.
"""
import logging
import boto3


class GluePyShellJobCreator:
    """
    A custom class to create and run AWS Glue PyShell jobs using boto3 directly.
    This bypasses the issues in Airflow's GlueJobOperator when creating PyShell jobs.
    """
    
    def __init__(
        self,
        job_name,
        role_name,
        script_location,
        glue_version='5.0',
        python_version='3.9',
        max_capacity=0.0625,
        default_arguments=None,
        tags=None,
        region_name='us-west-1',
        timeout=5
    ):
        """
        Initialize the Glue PyShell job creator.
        
        Args:
            job_name (str): Name of the Glue job
            role_name (str): IAM role name (not ARN)
            script_location (str): S3 location of the Python script
            glue_version (str): Glue version to use
            python_version (str): Python version to use
            max_capacity (float): Maximum capacity for the job
            default_arguments (dict): Default arguments for the job
            tags (dict): Tags to apply to the job
            region_name (str): AWS region name
            timeout (int): Job timeout in minutes
        """
        self.job_name = job_name
        self.role_name = role_name
        self.script_location = script_location
        self.glue_version = glue_version
        self.python_version = python_version
        self.max_capacity = max_capacity
        self.default_arguments = default_arguments or {}
        self.tags = tags or {}
        self.region_name = region_name
        self.timeout = timeout
        
        # Create boto3 clients
        self.glue_client = boto3.client('glue', region_name=self.region_name)
        self.iam_client = boto3.client('iam', region_name=self.region_name)
    
    def get_role_arn(self):
        """Get the IAM role ARN from the role name."""
        response = self.iam_client.get_role(RoleName=self.role_name)
        return response['Role']['Arn']
    
    def job_exists(self):
        """Check if the job already exists."""
        try:
            self.glue_client.get_job(JobName=self.job_name)
            logging.info(f"Job {self.job_name} already exists")
            return True
        except self.glue_client.exceptions.EntityNotFoundException:
            logging.info(f"Job {self.job_name} does not exist")
            return False
    
    def create_job_config(self):
        """Create the job configuration."""
        role_arn = self.get_role_arn()
        
        job_config = {
            'Name': self.job_name,
            'Role': role_arn,
            'ExecutionProperty': {'MaxConcurrentRuns': 1},
            'Command': {
                'Name': 'pythonshell',
                'ScriptLocation': self.script_location,
                'PythonVersion': self.python_version
            },
            'MaxCapacity': self.max_capacity,
            'GlueVersion': self.glue_version,
            'DefaultArguments': self.default_arguments,
            'Tags': self.tags,
            'Timeout': self.timeout
        }
        
        return job_config
    
    def create_job_if_not_exists(self):
        """Create the Glue job if it doesn't exist."""
        if not self.job_exists():
            job_config = self.create_job_config()
            logging.info(f"Creating job {self.job_name} with config: {job_config}")
            self.glue_client.create_job(**job_config)
            return True
        return False
    
    def run_job(self, arguments=None):
        """
        Run the Glue job.
        
        Args:
            arguments (dict): Arguments to pass to the job
            
        Returns:
            str: The job run ID
        """
        arguments = arguments or {}
        
        # Make sure the job exists
        self.create_job_if_not_exists()
        
        # Run the job
        logging.info(f"Starting job {self.job_name} with arguments: {arguments}")
        response = self.glue_client.start_job_run(
            JobName=self.job_name,
            Arguments=arguments
        )
        
        job_run_id = response['JobRunId']
        logging.info(f"Started job run with ID: {job_run_id}")
        return job_run_id
