import time
import boto3
import logging
from botocore.exceptions import ClientError

AWS_ACCOUNT_ID = '542605267262'
AWS_REGION = 'us-west-1'

DWH_PIPELINE_ALERTS_SNS_TOPIC_ARN = f'arn:aws:sns:{AWS_REGION}:{AWS_ACCOUNT_ID}:dwh-pipeline-alerts-jc'
GLUE_CONNECTION_POSTGRES = 'sfly-aws-dwh-sandbox-jc-mwaa-postgres-connection'
GLUE_ROLE_NAME = 'sfly-aws-dwh-sandbox-jc-mwaa-glue'
CODE_BUCKET = f'sfly-aws-dwh-sandbox-jc-mwaa-{AWS_REGION}-code'
CODE_PREFIX = 'code'

LOGIC_MODULE = 'dwh.jobs.schemas.schema_upgrade_glue'


def _check_job_exists(glue_client, job_name, logger):
    """Check if a Glue job exists."""
    try:
        glue_client.get_job(JobName=job_name)
        logger.info(f"Glue job {job_name} already exists")
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'EntityNotFoundException':
            logger.info(f"Glue job {job_name} does not exist")
            return False
        else:
            logger.error(f"Error checking job: {e}")
            raise


def _create_glue_job(glue_client, job_name, code_version, timeout, logger):
    """Create a new Glue job."""
    VERSIONED_PATH = f"{CODE_PREFIX}/{code_version}"

    logger.info(f"Creating Glue job {job_name}...")
    job_params = {
        'Name': job_name,
        'Role': f'arn:aws:iam::{AWS_ACCOUNT_ID}:role/{GLUE_ROLE_NAME}',
        'ExecutionProperty': {'MaxConcurrentRuns': 1},
        'Command': {'Name': 'glueetl', 'ScriptLocation': f's3://{CODE_BUCKET}/{VERSIONED_PATH}/scripts/glue/generic_entry.py'},
        'DefaultArguments': {
            '--enable-metrics': 'true',
            '--enable-continuous-cloudwatch-log': 'true',
            '--extra-py-files': f"s3://{CODE_BUCKET}/{VERSIONED_PATH}/dwh_pipeline_poc-{code_version}-py3-none-any.whl",
            '--python-modules-installer-option': '-r',
            '--additional-python-modules': f"s3://{CODE_BUCKET}/{VERSIONED_PATH}/requirements.txt",
        },
        'GlueVersion': '5.0',
        'NumberOfWorkers': 2,
        'WorkerType': 'G.1X',
        'Timeout': timeout,
    }

    try:
        glue_client.create_job(**job_params)
        logger.info(f"Successfully created Glue job {job_name}")
    except Exception as e:
        logger.error(f"Failed to create job: {e}")
        raise


def _run_glue_job(glue_client, job_name, schemas, timeout, logger):
    """Run a Glue job with the specified parameters."""
    logger.info(f"Starting Glue job {job_name}...")
    run_args = {'JobName': job_name}

    script_args = {
        '--module_name': LOGIC_MODULE,
        '--glue_connection_name': GLUE_CONNECTION_POSTGRES,
        '--glue_region': AWS_REGION,
        '--schemas': ','.join(schemas),
        '--ddl_bucket': CODE_BUCKET,
        '--ddl_prefix': CODE_PREFIX,
    }
    if DWH_PIPELINE_ALERTS_SNS_TOPIC_ARN is not None:
        script_args['--sns_topic_arn_alerts'] = DWH_PIPELINE_ALERTS_SNS_TOPIC_ARN

    run_args['Arguments'] = script_args

    if timeout:
        run_args['Timeout'] = timeout
    
    try:
        response = glue_client.start_job_run(**run_args)
        job_run_id = response['JobRunId']
        logger.info(f"Job started with run ID: {job_run_id}")
        return job_run_id
    except Exception as e:
        logger.error(f"Failed to start job: {e}")
        raise


def create_and_run_schema_upgrade_glue_job(
        job_name: str,
        schemas: list[str],
        code_version: str = '0.1.0',
        timeout: int = 5,
):
    """
    Check if a Glue job exists, create it if it doesn't, and run it.
    """
    glue_client = boto3.client('glue', region_name=AWS_REGION)
    logger = logging.getLogger(__name__)
    
    logger.info(f"Checking for job {job_name} in region {AWS_REGION}")
    
    # Check if job exists and create if needed
    job_exists = _check_job_exists(glue_client, job_name, logger)
    if not job_exists:
        _create_glue_job(glue_client, job_name, code_version, timeout, logger)

    # Run the job
    return _run_glue_job(glue_client, job_name, schemas, timeout, logger)


def _check_timeout(start_time, max_wait_time, job_run_id, logger):
    """Check if the job has exceeded the maximum wait time."""
    if max_wait_time and (time.time() - start_time) > max_wait_time:
        logger.warning(f"Maximum wait time of {max_wait_time} seconds exceeded. Job may still be running.")
        return True, {"JobRunState": "TIMEOUT", "JobRunId": job_run_id}
    return False, None


def _get_job_status(glue_client, job_name, job_run_id, prev_status, logger):
    """Get the current status of a Glue job."""
    try:
        response = glue_client.get_job_run(JobName=job_name, RunId=job_run_id)
        job_run = response['JobRun']
        job_status = job_run['JobRunState']

        # Log status changes or periodic updates
        if job_status != prev_status:
            logger.info(f"Job status changed: {prev_status} -> {job_status}")
        else:
            logger.info(f"Job status: {job_status}")

        return job_status, job_run
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise


def _log_job_completion(job_status, job_run, elapsed_time, logger):
    """Log information about the completed job."""
    logger.info(f"Job completed with status {job_status} in {elapsed_time:.2f} seconds")

    if job_status == 'SUCCEEDED':
        logger.info("Job completed successfully")
    elif job_status == 'FAILED':
        error_message = job_run.get('ErrorMessage', 'No error message available')
        logger.error(f"Job failed: {error_message}")
    elif job_status == 'TIMEOUT':
        logger.warning("Job timed out")
    elif job_status == 'STOPPED':
        logger.info("Job was manually stopped")


def monitor_glue_job(job_name: str, job_run_id: str, poll_interval: int = 30, max_wait_time=None):
    """
    Monitor a Glue job until it completes.

    Args:
        job_name (str): Name of the Glue job
        job_run_id (str): Run ID of the job to monitor
        poll_interval (int): Time in seconds between status checks
        max_wait_time (int, optional): Maximum time to wait in seconds, None for unlimited

    Returns:
        dict: The final job run information
    """
    glue_client = boto3.client('glue', region_name=AWS_REGION)
    logger = logging.getLogger(__name__)

    start_time = time.time()
    job_status = "UNKNOWN"
    logger.info(f"Monitoring Glue job {job_name} (Run ID: {job_run_id})")

    # States indicating the job is still running
    running_states = ['STARTING', 'RUNNING', 'STOPPING']

    while True:
        # Check if max wait time has been exceeded
        timed_out, timeout_result = _check_timeout(start_time, max_wait_time, job_run_id, logger)
        if timed_out:
            return timeout_result

        # Get current job status
        job_status, job_run = _get_job_status(glue_client, job_name, job_run_id, job_status, logger)

        # Exit loop if job is no longer running
        if job_status not in running_states:
            break

        # Sleep before next check
        time.sleep(poll_interval)

    # Log completion details
    elapsed_time = time.time() - start_time
    _log_job_completion(job_status, job_run, elapsed_time, logger)

    return job_run


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    job_name = 'schema-upgrade-job-test-2'
    job_run_id = create_and_run_schema_upgrade_glue_job(
        job_name=job_name,
        schemas=['dw_core'],
        code_version='0.1.0',
        timeout=5
    )
    print(f"Started job with run ID: {job_run_id}")
    print(f"Run details: : https://us-west-1.console.aws.amazon.com/gluestudio/home?region={AWS_REGION}#/job/{job_name}/run/{job_run_id}")

    # Monitor job until completion
    job_result = monitor_glue_job(
        job_name=job_name,
        job_run_id=job_run_id,
        poll_interval=10,  # Check every 15 seconds
        max_wait_time=600  # Wait up to 10 minutes
    )

    if job_result.get('JobRunState') == 'SUCCEEDED':
        print("✓ Job completed successfully")
    else:
        print(f"⚠ Job ended with status: {job_result.get('JobRunState')}")
