# SparkRouter

[![PyPI version](https://badge.fury.io/py/sparkrouter.svg)](https://badge.fury.io/py/sparkrouter)
[![Python](https://img.shields.io/pypi/pyversions/sparkrouter.svg)](https://pypi.org/project/sparkrouter/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

**Platform-agnostic job routing framework for Spark ETL pipelines.**

Write your ETL logic once, run it on Databricks, AWS Glue, EMR, or Docker containers.

## Why SparkRouter?

- **Write Once, Run Anywhere**: Same job code runs on multiple Spark platforms
- **Clean Architecture**: Factory + Template Method patterns keep code testable
- **Configuration-Driven**: JSON config via CLI, no code changes between environments

## Installation

```bash
uv add sparkrouter
# or
pip install sparkrouter
```

## Quick Start

### How It Works

```mermaid
flowchart LR
    A["Airflow DAG"] --> B["Entry Script"] --> C["Your Job Factory"] --> D["Your Job"]
```

1. **Airflow** (or any orchestrator) triggers a Spark platform job
2. The **entry script** routes to your code via `--module_name`
3. Your **factory** creates the job with dependencies
4. Your **job** runs the business logic

### Step 1: Write Your Job

```python
# my_etl_job.py
from sparkrouter import AbstractJob

class MyETLJob(AbstractJob):
    def execute_job(self, input_path: str, output_path: str) -> dict:
        # Your business logic here
        print(f"Processing {input_path} -> {output_path}")
        return {"records_processed": 1000}

    def on_success(self, results):
        print(f"Done: {results['records_processed']} records")

    def on_failure(self, error_message):
        print(f"Failed: {error_message}")
```

### Step 2: Write Your Factory

```python
# my_etl_job_factory.py
from sparkrouter import AbstractJobFactory
from my_etl_job import MyETLJob

class MyETLJobFactory(AbstractJobFactory):
    def create_job(self, **kwargs) -> MyETLJob:
        return MyETLJob()

def main(**kwargs):
    """Entry point called by SparkRouter."""
    factory = MyETLJobFactory()
    return factory.run(**kwargs)
```

### Step 3: Run Locally

No entry script needed - run directly from the installed package:

```bash
python -m sparkrouter.entry_points.container \
    --module_name my_etl_job_factory \
    --input_path "/data/input" \
    --output_path "/data/output"
```

---

## Platform Deployment

When deploying to Glue, Databricks, or EMR, those platforms require a script file at an S3/DBFS location. SparkRouter uses a **single entry script per platform** that routes to any of your jobs via `--module_name`. You create this script once, upload it once, and reuse it for all jobs.

### AWS Glue

**1. Create the entry script** (one time):

```python
# glue_entry.py
from sparkrouter.entry_points.glue import main

if __name__ == "__main__":
    main()
```

**2. Upload to S3** (one time):

```bash
aws s3 cp glue_entry.py s3://my-bucket/scripts/glue_entry.py
```

**3. Run any job** by specifying `--module_name`:

```python
GlueJobOperator(
    script_location='s3://my-bucket/scripts/glue_entry.py',
    script_args={
        '--module_name': 'mypackage.jobs.my_etl_job_factory',
        '--input_path': 's3://data/input/',
        '--output_path': 's3://data/output/',
    },
    default_arguments={
        '--additional-python-modules': 'sparkrouter,mypackage',
    },
)
```

### Databricks

**1. Create the entry script** (one time):

```python
# databricks_entry.py
from sparkrouter.entry_points.container import ContainerEntryPoint

class DatabricksEntryPoint(ContainerEntryPoint):
    @property
    def service_provider(self) -> str:
        return "DATABRICKS"

    def detect_spark(self) -> bool:
        return True  # Databricks always has Spark

def main(argv=None):
    return DatabricksEntryPoint().run(argv)

if __name__ == "__main__":
    main()
```

**2. Upload to DBFS** (one time):

```bash
databricks fs cp databricks_entry.py dbfs:/scripts/databricks_entry.py
```

**3. Run any job** by specifying `--module_name`:

```python
DatabricksSubmitRunOperator(
    spark_python_task={
        'python_file': 'dbfs:/scripts/databricks_entry.py',
        'parameters': [
            '--module_name', 'mypackage.jobs.my_etl_job_factory',
            '--input_path', 's3://data/input/',
            '--output_path', 's3://data/output/',
        ],
    },
    libraries=[
        {'pypi': {'package': 'sparkrouter'}},
        {'pypi': {'package': 'mypackage'}},
    ],
)
```

### EMR

**1. Create the entry script** (one time):

```python
# emr_entry.py
import os
from sparkrouter.entry_points.container import ContainerEntryPoint

class EMREntryPoint(ContainerEntryPoint):
    @property
    def service_provider(self) -> str:
        return "EMR"

    def add_platform_context(self, args):
        args = super().add_platform_context(args)
        args['region'] = os.environ.get('AWS_REGION')
        return args

    def detect_spark(self) -> bool:
        return True  # EMR always has Spark

def main(argv=None):
    return EMREntryPoint().run(argv)

if __name__ == "__main__":
    main()
```

**2. Upload to S3** (one time):

```bash
aws s3 cp emr_entry.py s3://my-bucket/scripts/emr_entry.py
```

**3. Run any job** via spark-submit:

```bash
spark-submit s3://my-bucket/scripts/emr_entry.py \
    --module_name mypackage.jobs.my_etl_job_factory \
    --input_path s3://data/input/ \
    --output_path s3://data/output/
```

---

## Examples

See the [examples](examples/) directory:

- [Simple ETL Job](examples/simple_etl/) - Basic job with factory pattern
- [Airflow DAGs](examples/airflow/) - Glue and Databricks DAG examples

## License

Apache License 2.0
