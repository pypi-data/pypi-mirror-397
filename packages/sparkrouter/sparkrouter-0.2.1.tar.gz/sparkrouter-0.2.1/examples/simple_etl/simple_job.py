"""
Simple ETL Job Example
======================

A minimal example showing the SparkRouter job pattern.
"""

from typing import Any

from sparkrouter import AbstractJob


class SimpleETLJob(AbstractJob):
    """A simple ETL job that processes data."""

    def execute_job(
        self,
        input_path: str,
        output_path: str,
        filter_column: str = "status",
        filter_value: str = "active",
    ) -> dict:
        """
        Execute the ETL logic.

        Args:
            input_path: Path to read input data from.
            output_path: Path to write output data to.
            filter_column: Column to filter on.
            filter_value: Value to filter for.

        Returns:
            Dict with job results/metrics.
        """
        print(f"Reading data from: {input_path}")
        print(f"Filtering where {filter_column} = '{filter_value}'")
        print(f"Writing results to: {output_path}")

        # In a real job, you would use Spark:
        # df = spark.read.parquet(input_path)
        # filtered = df.filter(df[filter_column] == filter_value)
        # filtered.write.parquet(output_path)

        return {
            "input_path": input_path,
            "output_path": output_path,
            "records_processed": 1000,
            "records_written": 850,
        }

    def on_success(self, results: Any) -> None:
        """Handle successful job completion."""
        print(
            f"Success: processed {results['records_processed']} records, "
            f"wrote {results['records_written']} to {results['output_path']}"
        )

    def on_failure(self, error_message: str) -> None:
        """Handle job failure."""
        print(f"Failed: {error_message}")
