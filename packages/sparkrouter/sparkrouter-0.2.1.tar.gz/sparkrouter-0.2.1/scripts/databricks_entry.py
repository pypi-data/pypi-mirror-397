#!/usr/bin/env python
"""
Databricks Entry Point Script
=============================

Upload this script to DBFS and reference it in your Databricks jobs.

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

from sparkrouter.entry_points.databricks import main

if __name__ == "__main__":
    main()
