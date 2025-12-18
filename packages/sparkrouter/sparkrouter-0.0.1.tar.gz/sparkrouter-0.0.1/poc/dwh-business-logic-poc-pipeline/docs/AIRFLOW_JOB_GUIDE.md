# Guide: Writing and Running Jobs with Airflow (MWAA) and Databricks

This guide is for junior MWAA/Airflow developers. It covers how to:
- Write a new job
- Test it locally
- Create a Databricks DAG for Airflow

---

## 1. Writing a New Job

Jobs are Python classes that encapsulate business logic. To add a new job:

1. **Create a Job Logic Class**
   - Location: `src/dwh/jobs/<your_job>/<your_job>_job.py`
   - Inherit from a base job class if available.
   - Implement a `run()` method.

   ```python
   # src/dwh/jobs/example/example_job.py
   class ExampleJob:
       def __init__(self, ...):
           # ...initialize dependencies...

       def run(self, **kwargs):
           # ...job logic here...
           print("Job ran successfully")
   ```

2. **Create a Job Factory**
   - Location: `src/dwh/jobs/<your_job>/<your_job>_job_factory.py`
   - Responsible for assembling the job with required services.

   ```python
   # src/dwh/jobs/example/example_job_factory.py
   from dwh.jobs.example.example_job import ExampleJob

   class ExampleJobFactory:
       def create_job(self, **kwargs):
           # ...assemble dependencies...
           return ExampleJob(...)
   ```

---

## 2. Testing Locally

You can test jobs locally using Docker Compose.

1. **Write an Integration Test**
   - Location: `tests/integration/dwh/jobs/<your_job>/test_<your_job>_job_integration.py`
   - Use `subprocess` to invoke the job via Docker Compose.

   ```python
   import subprocess

   def test_example_job():
       cmd = [
           "docker-compose", "-f", "docker/docker-compose.yml", "run", "--rm",
           "python-submit",
           "--module_name", "dwh.jobs.example.example_job_factory",
           "--example_job", '{"config_key": "value"}'
       ]
       process = subprocess.run(cmd, capture_output=True, text=True)
       assert process.returncode == 0
       assert "Job ran successfully" in process.stdout
   ```

2. **Run the Test**
   ```sh
   pytest tests/integration/dwh/jobs/example/test_example_job_integration.py
   ```

---

## 3. Creating a Databricks DAG

To orchestrate your job on Databricks via Airflow:

1. **Create a DAG File**
   - Location: `dags/<your_job>_databricks_dag.py`

2. **Use the DatabricksSubmitRunOperator**
   - Configure the operator to run your job on Databricks.

   ```python
   from airflow import DAG
   from airflow.providers.databricks.operators.databricks import DatabricksSubmitRunOperator
   from datetime import datetime

   default_args = {
       'owner': 'airflow',
       'start_date': datetime(2024, 1, 1),
   }

   with DAG('example_job_databricks', default_args=default_args, schedule_interval=None) as dag:
       submit_run = DatabricksSubmitRunOperator(
           task_id='run_example_job',
           databricks_conn_id='databricks_default',
           new_cluster={
               'spark_version': '11.3.x-scala2.12',
               'node_type_id': 'i3.xlarge',
               'num_workers': 2,
           },
           spark_python_task={
               'python_file': 'dbfs:/path/to/your/job_script.py',
               'parameters': ['--config', '{"config_key": "value"}']
           }
       )
   ```

3. **Deploy the DAG**
   - Place the DAG file in your Airflow `dags/` directory.
   - Ensure your job code is available to Databricks (e.g., uploaded to DBFS).

---

## Tips

- Use factories to inject dependencies and keep job logic portable.
- Test locally before deploying to Airflow or Databricks.
- Use Airflow connections for credentials and cluster configuration.

---

