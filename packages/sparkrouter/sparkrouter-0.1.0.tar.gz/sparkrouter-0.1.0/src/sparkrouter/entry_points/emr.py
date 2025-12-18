#!/usr/bin/env python
"""
Amazon EMR Entry Point
======================

Entry point for running SparkRouter jobs on Amazon EMR.

This script serves as a unified entry point for running Python modules as
EMR steps. It handles EMR-specific environment detection.

Usage:
    aws emr add-steps --cluster-id j-XXXXX --steps Type=Spark,Name="MyJob",\\
        ActionOnFailure=CONTINUE,\\
        Args=[--deploy-mode,cluster,--master,yarn,\\
              s3://bucket/scripts/emr/entry.py,\\
              --module_name,myproject.jobs.my_job_factory,\\
              --my_job,'{"input_path": "s3://..."}']
"""

import os
from typing import Dict

from sparkrouter.entry_points.base import BaseEntryPoint


class EMREntryPoint(BaseEntryPoint):
    """Entry point for Amazon EMR jobs."""

    @property
    def service_provider(self) -> str:
        return "EMR"

    def add_platform_context(self, args: Dict[str, any]) -> Dict[str, any]:
        """Add EMR-specific context from environment variables."""
        if 'region' not in args:
            args['region'] = os.environ.get(
                'AWS_REGION',
                os.environ.get('AWS_DEFAULT_REGION')
            )

        # EMR cluster ID if available
        cluster_id = os.environ.get('EMR_CLUSTER_ID')
        if cluster_id:
            args['emr_cluster_id'] = cluster_id

        return args

    def detect_spark(self) -> bool:
        # EMR Spark jobs always have Spark available
        return True


def main(argv=None):
    """Main entry point for EMR jobs."""
    entry_point = EMREntryPoint()
    return entry_point.run(argv)


if __name__ == "__main__":
    main()
