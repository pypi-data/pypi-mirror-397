"""
Simple ETL Job Factory
======================

Factory for creating SimpleETLJob instances.
"""

from sparkrouter import AbstractJobFactory

from examples.simple_etl.simple_job import SimpleETLJob


class SimpleETLJobFactory(AbstractJobFactory):
    """Factory for creating SimpleETLJob instances."""

    def create_job(self, **kwargs) -> SimpleETLJob:
        """Create a SimpleETLJob."""
        return SimpleETLJob()


def main(**kwargs):
    """
    Entry point for the job.

    Called by platform entry points via dynamic import.
    """
    factory = SimpleETLJobFactory()
    return factory.run(**kwargs)


# Example CLI invocation:
#
# python -m sparkrouter.entry_points.container \
#     --module_name examples.simple_etl.simple_job_factory \
#     --input_path "s3://bucket/input/" \
#     --output_path "s3://bucket/output/"
