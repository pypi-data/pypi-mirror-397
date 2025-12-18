# Job Framework Documentation

[//]: # (code versions)

[//]: # (scripts)

[//]: # (notifications)

## Generic Entry Point

The `entry_point` scripts serve as a standardized job launcher for use by Airflow DAGs:

There is an entry point for runtime environment; `Databricks`, `AWS Glue`, etc.

GLUE:
```
scripts/glue/generic_entry.py'
```

DATABRICKS:
```
scripts/databricks/generic_entry.py"
```

These scripts are designed to be generic and reusable across different job types, allowing for consistent job execution regardless of the underlying service.


## Architecture Foundation: AbstractJob and AbstractJobFactory
The job framework is built on two key abstractions:

* AbstractJobFactory
* AbstractJob

entry_point scripts use these abstractions to create and run jobs in a service-agnostic manner.

### AbstractJobFactory

`AbstractJobFactory` decouples job creation from execution environments:
* Creates appropriate job instances based on configuration
* Handles environment-specific setup (credentials, connections)
* Isolates service-specific dependencies

```python
# TODO
```

The factory pattern ensures service-specific code stays out of job implementations, making jobs portable across environments.

This approach provides consistent job execution regardless of environment and simplifies integration.


### AbstractJob
`AbstractJob` serves as the base class for all job implementations, providing:
* Common interface for job execution via the `run()` method
* Standard logging and error handling
* Configuration management
* Job lifecycle hooks (setup, execute, teardown)

```python
# TODO
```


## Example: Simple Glue Operator in MWAA

```python

entry_point = "s3://code-bucket/code-prefix/scripts/glue/generic_entry.py"
wheel = "s3://code-bucket/code-prefix/dwh_pipeline_poc-0.1.0-py3-none-any.whl"
job_factory = "dwh.jobs.spark_example.spark_example_job_factory"

dag = DAG(
    "spark_glue_example",
    default_args={},
    dagrun_timeout=timedelta(minutes=10),
    schedule=None,
    catchup=False,
    params={
        "code_version": Param("0.1.0", type="string", description="Version of the code to run"),
        'notification_service_type': Param("NOOP", type="string", description="Notification service to use. Required. Options are [NOOP, SNS]")
    })    
run_glue_job = GlueJobOperator(
    task_id='glue_job',
    job_name="glue_example",
    script_location=entry_point,
    script_args={
        "--module_name": job_factory,
        "--notification_service_type": "{{ params.notification_service_type }}"
    },
    s3_bucket="code-bucket",
    iam_role_name="glue-job-role",
    run_job_kwargs={
        'Timeout': 5
    },
    create_job_kwargs={
        'GlueVersion': '5.0',
        'NumberOfWorkers': 2,
        'WorkerType': 'G.1X',
        'DefaultArguments': {
            '--extra-py-files': wheel,
            # uncomment to install additional Python modules
            # '--python-modules-installer-option': '-r',
            # '--additional-python-modules': f's3://code-bucket/code-prefix//requirements.txt',
        }
    },
    dag=dag
)

wait_for_glue_job = GlueJobSensor(
    task_id='wait_for_glue_job',
    job_name="glue_test",
    run_id="{{ task_instance.xcom_pull(task_ids='glue_job', key='return_value') }}",
    dag=dag
)

run_glue_job >> wait_for_glue_job
```

## Example: Simple Databricks Operator

```python
entry_point = "s3://code-bucket/code-prefix/scripts/databricks/generic_entry.py"
wheel = "s3://code-bucket/code-prefix/dwh_pipeline_poc-0.1.0-py3-none-any.whl"
job_factory = "dwh.jobs.spark_example.spark_example_job_factory"
databricks_connection_name = "databricks"

with DAG(
    dag_id="test_databricks",
    default_args={},
    schedule=None,
    catchup=False,
    params={
        "code_version": Param("0.1.0", type="string", description="Version of the code to run"),
        'notification_service_type': Param("NOOP", type="string", description="Notification service to use. Required. Options are [NOOP, SNS]")
    }
) as dag:

    cluster_config = {
        "spark_version": "15.4.x-scala2.12",
        "node_type_id": "mgd-fleet.xlarge",
        "driver_node_type_id": "mgd-fleet.xlarge",
        "num_workers": 1,
        "spark_env_vars": {
            "PYSPARK_PYTHON": "/databricks/python3/bin/python3",
            "ENV": "dev"
        },
        "aws_attributes": {
            "instance_profile_arn": "your-instance-profile-arn",
        }
    }

    databricks_task = DatabricksSubmitRunOperator(
        task_id="run_simple_job",
        databricks_conn_id="databricks_consumer",
        json={
            "run_name": "test_databricks",
            "new_cluster": cluster_config,
            "timeout_seconds": 600,
            "spark_python_task": {
                "python_file": entry_point,
                "parameters": [
                    "--module_name", job_factory,
                    "--notification_service_type", "{{ params.notification_service_type }}",
                    "--databricks_connection_name", databricks_connection_name,                    
                ]
            },
            "libraries": [
                {
                    "whl": wheel
                }
            ],
            # allows users in consumer-developers group to see the job run details in Databricks UI
            "access_control_list": [{
                "group_name": "consumer-developers",
                "permission_level": "CAN_VIEW"
            }]
        },
        retries=0,
        retry_delay=timedelta(minutes=5),
        do_xcom_push=True,
    )
```


## Running Jobs Locally

* TODO
