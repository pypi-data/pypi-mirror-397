#!/usr/bin/env python
"""
Amazon EMR Entry Point Script
=============================

Upload this script to S3 and reference it in your EMR steps.

This script demonstrates how to customize the entry point for your platform
by subclassing ContainerEntryPoint and overriding add_platform_context().

Deployment:
    aws s3 cp emr_entry.py s3://your-bucket/scripts/emr_entry.py

Usage:
    spark-submit s3://your-bucket/scripts/emr_entry.py \
        --module_name mypackage.jobs.my_job_factory \
        --input_path s3://data/input/ \
        --output_path s3://data/output/

Requirements:
    - sparkrouter must be installed on EMR cluster (bootstrap action or --py-files)
"""

import os
from sparkrouter.entry_points.container import ContainerEntryPoint


class EMREntryPoint(ContainerEntryPoint):
    """Custom entry point for Amazon EMR with platform-specific context."""

    @property
    def service_provider(self) -> str:
        return "EMR"

    def add_platform_context(self, args):
        """Add EMR-specific context from environment variables."""
        args = super().add_platform_context(args)

        # Add AWS region if not already provided
        if 'region' not in args:
            args['region'] = os.environ.get(
                'AWS_REGION',
                os.environ.get('AWS_DEFAULT_REGION')
            )

        # Add EMR cluster ID if available
        cluster_id = os.environ.get('EMR_CLUSTER_ID')
        if cluster_id:
            args['emr_cluster_id'] = cluster_id

        return args

    def detect_spark(self) -> bool:
        """EMR Spark jobs always have Spark available."""
        return True


def main(argv=None):
    """Main entry point for EMR jobs."""
    return EMREntryPoint().run(argv)


if __name__ == "__main__":
    main()
