#!/usr/bin/env python
"""
AWS Glue Entry Point
====================

Entry point for running SparkRouter jobs on AWS Glue.

This script serves as a unified entry point for running Python modules as
AWS Glue jobs. It abstracts away Glue-specific setup and handles
environment detection.

Usage from MWAA/Airflow:
    task = GlueJobOperator(
        task_id='process_data',
        job_name='data_processing_job',
        script_location='s3://bucket/scripts/glue/entry.py',
        script_args={
            '--module_name': 'myproject.jobs.my_job_factory',
            '--my_job': '{"input_path": "s3://...", "output_path": "s3://..."}'
        }
    )
"""

import os
from typing import Dict

from sparkrouter.entry_points.base import BaseEntryPoint


class GlueEntryPoint(BaseEntryPoint):
    """Entry point for AWS Glue jobs."""

    @property
    def service_provider(self) -> str:
        return "GLUE"

    @property
    def reserved_args(self) -> set:
        # Glue adds these system arguments
        return {'module_name', 'JOB_ID', 'JOB_RUN_ID', 'JOB_NAME'}

    def add_platform_context(self, args: Dict[str, any]) -> Dict[str, any]:
        """Add Glue-specific context from environment variables."""
        if 'environment' not in args:
            args['environment'] = os.environ.get('ENVIRONMENT')

        if 'region' not in args:
            args['region'] = os.environ.get(
                'AWS_REGION',
                os.environ.get('AWS_DEFAULT_REGION')
            )

        return args

    def detect_spark(self) -> bool:
        """Detect Spark in Glue environment."""
        # Check Glue-specific environment variable
        if os.environ.get("GLUE_COMMAND_CRITERIA", "").lower() == "glueetl":
            return True

        # Check PYTHONPATH for pyspark
        pythonpath = os.environ.get("PYTHONPATH", "")
        for path in pythonpath.split(os.pathsep):
            if "pyspark" in path.lower():
                return True

        # Fall back to import check
        return super().detect_spark()


def main(argv=None):
    """Main entry point for AWS Glue jobs."""
    entry_point = GlueEntryPoint()
    return entry_point.run(argv)


if __name__ == "__main__":
    main()
