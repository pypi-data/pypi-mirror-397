#!/usr/bin/env python
"""
AWS Glue Entry Point Script
===========================

Upload this script to S3 and reference it in your Glue jobs.

Deployment:
    aws s3 cp glue_entry.py s3://your-bucket/scripts/glue_entry.py

Usage in Airflow:
    GlueJobOperator(
        script_location='s3://your-bucket/scripts/glue_entry.py',
        script_args={
            '--module_name': 'mypackage.jobs.my_job_factory',
            '--my_job': '{"config": "value"}',
        },
    )

Requirements:
    - sparkrouter must be installed in the Glue job environment
    - Add to Glue job: --additional-python-modules sparkrouter
"""

from sparkrouter.entry_points.glue import main

if __name__ == "__main__":
    main()
