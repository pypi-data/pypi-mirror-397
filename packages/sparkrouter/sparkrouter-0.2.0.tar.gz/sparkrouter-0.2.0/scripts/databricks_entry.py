#!/usr/bin/env python
"""
Databricks Entry Point Script
=============================

Upload this script to DBFS and reference it in your Databricks jobs.

This script demonstrates how to customize the entry point for your platform
by subclassing ContainerEntryPoint and overriding methods as needed.

Deployment:
    databricks fs cp databricks_entry.py dbfs:/scripts/databricks_entry.py

Usage in Airflow:
    DatabricksSubmitRunOperator(
        spark_python_task={
            'python_file': 'dbfs:/scripts/databricks_entry.py',
            'parameters': [
                '--module_name', 'mypackage.jobs.my_job_factory',
                '--input_path', 's3://data/input/',
                '--output_path', 's3://data/output/',
            ],
        },
        libraries=[
            {'pypi': {'package': 'sparkrouter'}},
        ],
    )

Requirements:
    - sparkrouter must be installed on the cluster (cluster or job libraries)
"""

from sparkrouter.entry_points.container import ContainerEntryPoint


class DatabricksEntryPoint(ContainerEntryPoint):
    """Custom entry point for Databricks with platform-specific context."""

    @property
    def service_provider(self) -> str:
        return "DATABRICKS"

    def detect_spark(self) -> bool:
        """Databricks always has Spark available."""
        return True

    # Add custom platform context if needed:
    # def add_platform_context(self, args):
    #     args = super().add_platform_context(args)
    #     args['workspace_url'] = os.environ.get('DATABRICKS_HOST')
    #     return args


def main(argv=None):
    """Main entry point for Databricks jobs."""
    return DatabricksEntryPoint().run(argv)


if __name__ == "__main__":
    main()
