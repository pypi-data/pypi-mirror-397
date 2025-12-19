#!/usr/bin/env python
"""
Container Entry Point
=====================

Entry point for running SparkRouter jobs in Docker containers.

This script serves as a unified entry point for running Python modules in
containerized environments (Docker, Kubernetes, ECS, etc.).

Usage:
    docker run my-spark-image python -m sparkrouter.entry_points.container \
        --module_name myproject.jobs.my_job_factory \
        --my_job '{"input_path": "s3://...", "output_path": "s3://..."}'
"""

from sparkrouter.entry_points.base import BaseEntryPoint


class ContainerEntryPoint(BaseEntryPoint):
    """Entry point for containerized jobs."""

    @property
    def service_provider(self) -> str:
        return "CONTAINER"


def main(argv=None):
    """Main entry point for container jobs."""
    entry_point = ContainerEntryPoint()
    return entry_point.run(argv)


if __name__ == "__main__":
    main()
