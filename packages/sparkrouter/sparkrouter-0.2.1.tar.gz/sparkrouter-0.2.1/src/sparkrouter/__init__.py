"""
SparkRouter - Platform-agnostic job routing framework for Spark ETL pipelines.

Write your ETL logic once, run it on Databricks, AWS Glue, EMR, or Docker containers.

Quick Start:
    from sparkrouter import AbstractJob, AbstractJobFactory

    class MyETLJob(AbstractJob):
        def execute_job(self, input_path: str, output_path: str) -> dict:
            # Your business logic here
            return {"records": 100}

        def on_success(self, results):
            print(f"Processed {results['records']} records")

        def on_failure(self, error_message):
            print(f"Failed: {error_message}")

    class MyETLJobFactory(AbstractJobFactory):
        def create_job(self, **kwargs):
            return MyETLJob()

    def main(**kwargs):
        factory = MyETLJobFactory()
        return factory.run(**kwargs)
"""

from sparkrouter.version import __version__
from sparkrouter.job.abstract_job import AbstractJob
from sparkrouter.job.abstract_job_factory import AbstractJobFactory

__all__ = [
    "__version__",
    "AbstractJob",
    "AbstractJobFactory",
]
