#!/usr/bin/env python
"""
Databricks Entry Point
======================

Entry point for running SparkRouter jobs on Databricks.

This script serves as a unified entry point for running Python modules as
Databricks jobs. It abstracts away Databricks-specific setup, allowing jobs
to be written as standard Python modules.

Usage from MWAA/Airflow:
    task = DatabricksSubmitRunOperator(
        task_id='process_data',
        databricks_conn_id='databricks_default',
        spark_python_task={
            'python_file': 'dbfs:/scripts/databricks/entry.py',
            'parameters': [
                '--module_name', 'myproject.jobs.my_job_factory',
                '--my_job', '{"input_path": "s3://...", "output_path": "s3://..."}'
            ]
        }
    )
"""

from sparkrouter.entry_points.base import BaseEntryPoint


class DatabricksEntryPoint(BaseEntryPoint):
    """Entry point for Databricks jobs."""

    @property
    def service_provider(self) -> str:
        return "DATABRICKS"

    def detect_spark(self) -> bool:
        # Databricks always has Spark available
        return True


def main(argv=None):
    """Main entry point for Databricks jobs."""
    entry_point = DatabricksEntryPoint()
    return entry_point.run(argv)


if __name__ == "__main__":
    main()
