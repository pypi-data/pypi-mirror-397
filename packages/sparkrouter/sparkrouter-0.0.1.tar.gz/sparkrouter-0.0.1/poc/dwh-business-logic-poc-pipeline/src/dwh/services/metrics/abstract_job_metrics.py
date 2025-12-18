"""
Abstract base class for job metrics collection.

This module defines the common metrics structure that ALL jobs must provide.
Job-specific metrics should be placed in the 'payload' section.

The common structure enables:
1. Cross-job dashboards and comparisons
2. Unified SLA monitoring
3. Cost analysis across all jobs
4. Environment health overview

Usage:
    class MyJobMetrics(AbstractJobMetrics):
        def __init__(self):
            super().__init__(job_name="my_job")
            # Add job-specific fields
            self.my_custom_field = 0

        def get_payload(self) -> dict:
            return {
                "my_custom_field": self.my_custom_field,
                # ... other job-specific metrics
            }
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, List


@dataclass
class AbstractJobMetrics(ABC):
    """
    Base class for job metrics collection.

    All jobs MUST provide these common fields for cross-job analysis.
    Job-specific metrics go in the payload via get_payload().
    """

    # === REQUIRED: Job Identity ===
    job_name: str = None  # MUST be set by subclass

    # === Job Run Identity ===
    job_run_id: str = None  # Spark application ID or equivalent

    # === Status ===
    job_status: str = None  # SUCCESS, FAILED

    # === Timing ===
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime = None

    # === Execution Context ===
    service_provider: str = None  # GLUE, DATABRICKS, EMR, CONTAINER
    environment: str = None       # sandbox, dev, prod
    region: str = None            # us-west-1, us-east-1, etc.
    created_by: str = None        # User/system that triggered the job

    # === Data Range (for ETL jobs) ===
    start_date: str = None  # User-requested start date for data processing
    end_date: str = None    # User-requested end date for data processing

    # === Data Paths ===
    source_base_path: str = None  # Base path where data was read from
    sink_base_path: str = None    # Base path where data was written to

    # === ETL Summary (high-level for cross-job comparison) ===
    records_read: int = 0
    records_written: int = 0
    records_dropped: int = 0
    bytes_written: int = 0

    # === Phase Durations (optional but recommended for ETL jobs) ===
    extract_duration_seconds: float = 0.0
    transform_duration_seconds: float = 0.0
    load_duration_seconds: float = 0.0

    # === Phase Timestamps (for timeline visualization) ===
    extract_start_time: datetime = None
    extract_end_time: datetime = None
    transform_start_time: datetime = None
    transform_end_time: datetime = None
    load_start_time: datetime = None
    load_end_time: datetime = None

    # === Resource Utilization ===
    spark_executor_count: int = 0
    spark_executor_memory_gb: int = 0
    spark_driver_memory_gb: int = 0
    glue_dpu_seconds: float = 0.0

    # === Drop Reasons (common across ETL jobs) ===
    drop_reasons: Dict[str, int] = field(default_factory=dict)

    def record_drop(self, reason: str, count: int = 1):
        """Record dropped records with reason"""
        if reason not in self.drop_reasons:
            self.drop_reasons[reason] = 0
        self.drop_reasons[reason] += count

    def complete(self):
        """Mark job as complete"""
        self.end_time = datetime.utcnow()

    def get_duration_seconds(self) -> float:
        """Get job duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return (datetime.utcnow() - self.start_time).total_seconds()

    @staticmethod
    def _dict_to_array(
        d: Dict[str, Any],
        key_name: str,
        value_name: str = None
    ) -> List[Dict[str, Any]]:
        """
        Convert a dict with dynamic keys to an array of objects.

        This makes the data OpenSearch-aggregation-friendly.

        Args:
            d: Dictionary to convert (e.g., {"parser_a": 100, "parser_b": 200})
            key_name: Name for the key field (e.g., "name", "reason", "category")
            value_name: Name for the value field if values are scalars (e.g., "count", "bytes").
                       If None, assumes values are dicts and merges them.

        Returns:
            Array of objects with key_name field added.

        Examples:
            # Scalar values:
            _dict_to_array({"a": 1, "b": 2}, "reason", "count")
            -> [{"reason": "a", "count": 1}, {"reason": "b", "count": 2}]

            # Dict values:
            _dict_to_array({"x": {"records": 10}}, "name")
            -> [{"name": "x", "records": 10}]
        """
        result = []
        for key, value in d.items():
            if value_name is not None:
                result.append({key_name: key, value_name: value})
            elif isinstance(value, dict):
                result.append({key_name: key, **value})
            else:
                result.append({key_name: key, "value": value})
        return result

    @abstractmethod
    def get_payload(self) -> Dict[str, Any]:
        """
        Return job-specific metrics as a dictionary.

        This is where job-specific fields that don't fit the common schema go.
        The payload is indexed as-is in the job-specific OpenSearch index.

        Returns:
            Dictionary of job-specific metrics
        """
        raise NotImplementedError("Subclasses must implement get_payload()")

    def get_summary(self) -> str:
        """
        Generate human-readable summary report.

        Subclasses should override to add job-specific details.
        """
        duration = self.get_duration_seconds()
        total_dropped = sum(self.drop_reasons.values())

        report = [
            f"\n{'='*80}",
            f"JOB METRICS SUMMARY: {self.job_name}",
            f"{'='*80}",
            f"Job Run ID: {self.job_run_id or 'N/A'}",
            f"Status: {self.job_status or 'N/A'}",
            f"Platform: {self.service_provider or 'N/A'}",
            f"Environment: {self.environment or 'N/A'}",
            f"Region: {self.region or 'N/A'}",
            f"Date Range: {self.start_date or 'N/A'} to {self.end_date or 'N/A'}",
            f"Created By: {self.created_by or 'N/A'}",
            f"Total Duration: {duration:.2f} seconds",
            "",
            "ETL SUMMARY:",
            f"  Records read: {self.records_read:,}",
            f"  Records written: {self.records_written:,}",
            f"  Records dropped: {total_dropped:,}",
            f"  Bytes written: {self.bytes_written:,}",
            "",
            "PHASE DURATIONS:",
            f"  Extract: {self.extract_duration_seconds:.2f} seconds",
            f"  Transform: {self.transform_duration_seconds:.2f} seconds",
            f"  Load: {self.load_duration_seconds:.2f} seconds",
        ]

        if total_dropped > 0:
            report.extend([
                "",
                f"DROPPED RECORDS: {total_dropped:,}",
                "  Breakdown by reason:",
            ])
            for reason, count in sorted(self.drop_reasons.items(), key=lambda x: -x[1]):
                percentage = (count / self.records_read * 100) if self.records_read > 0 else 0
                report.append(f"    - {reason}: {count:,} ({percentage:.2f}%)")

        # Calculate success rate
        if self.records_read > 0:
            success_rate = (self.records_written / self.records_read) * 100
            report.extend([
                "",
                "SUCCESS RATE:",
                f"  {self.records_written:,} / {self.records_read:,} records processed ({success_rate:.2f}%)",
            ])

        report.append(f"{'='*80}")

        return "\n".join(report)

    def get_json(self) -> dict:
        """
        Get metrics as JSON-serializable dict.

        Returns a standardized structure with:
        - Common fields at the top level
        - Job-specific metrics in the 'payload' section

        This structure is what gets published to OpenSearch.
        """
        result = {
            # Job identity
            "job_name": self.job_name,
            "job_run_id": self.job_run_id,
            "job_status": self.job_status,

            # Timing
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": self.get_duration_seconds(),

            # Execution context
            "service_provider": self.service_provider,
            "environment": self.environment,
            "region": self.region,
            "created_by": self.created_by,

            # Data range
            "start_date": self.start_date,
            "end_date": self.end_date,

            # Data paths
            "source_base_path": self.source_base_path,
            "sink_base_path": self.sink_base_path,

            # ETL summary (for cross-job comparison)
            "records_read": self.records_read,
            "records_written": self.records_written,
            "records_dropped": sum(self.drop_reasons.values()),
            "bytes_written": self.bytes_written,

            # Phase timings
            "phases": {
                "extract": {
                    "start_time": self.extract_start_time.isoformat() if self.extract_start_time else None,
                    "end_time": self.extract_end_time.isoformat() if self.extract_end_time else None,
                    "duration_seconds": self.extract_duration_seconds,
                },
                "transform": {
                    "start_time": self.transform_start_time.isoformat() if self.transform_start_time else None,
                    "end_time": self.transform_end_time.isoformat() if self.transform_end_time else None,
                    "duration_seconds": self.transform_duration_seconds,
                },
                "load": {
                    "start_time": self.load_start_time.isoformat() if self.load_start_time else None,
                    "end_time": self.load_end_time.isoformat() if self.load_end_time else None,
                    "duration_seconds": self.load_duration_seconds,
                },
            },

            # Drop reasons (array format for OpenSearch aggregation)
            "drop_reasons": self._dict_to_array(self.drop_reasons, "reason", "count"),

            # Job-specific payload
            "payload": self.get_payload(),
        }

        # Add resources section if any resource metrics are set
        if (self.spark_executor_count > 0 or self.spark_executor_memory_gb > 0 or
                self.spark_driver_memory_gb > 0 or self.glue_dpu_seconds > 0):
            result["resources"] = {
                "spark_executor_count": self.spark_executor_count,
                "spark_executor_memory_gb": self.spark_executor_memory_gb,
                "spark_driver_memory_gb": self.spark_driver_memory_gb,
                "glue_dpu_seconds": self.glue_dpu_seconds,
            }

        return result
