"""
Job metrics collector for transform_images job.

Extends AbstractJobMetrics with transform_images-specific metrics:
- Extract: partition details, corrupt records, event time range
- Transform: data type breakdown, decryption failures
- Load: category-based output, dropped records file
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any
from dwh.services.metrics.abstract_job_metrics import AbstractJobMetrics


@dataclass
class TransformImagesJobMetrics(AbstractJobMetrics):
    """
    Metrics collector for TransformImagesJob.

    Inherits common fields from AbstractJobMetrics and adds
    transform_images-specific metrics in the payload.
    """

    # Override job_name default
    job_name: str = "transform_images"

    # === Extract-specific metrics ===
    extract_partitions_requested: int = 0
    extract_partitions_found: int = 0
    extract_partitions_empty: int = 0
    extract_corrupt_records: int = 0
    extract_null_eventtime: int = 0
    extract_null_data: int = 0
    extract_records_after_filter: int = 0
    extract_min_event_time: str = None  # ISO timestamp of earliest record
    extract_max_event_time: str = None  # ISO timestamp of latest record
    extract_event_time_range_hours: float = 0.0

    # === Transform-specific metrics ===
    transform_records_input: int = 0
    transform_records_output: int = 0
    transform_decryption_failures: int = 0
    transform_null_critical_fields: int = 0
    transform_data_types: Dict[str, Dict[str, int]] = field(default_factory=dict)

    # === Load-specific metrics ===
    load_records_input: int = 0
    load_partitions_written: int = 0
    load_files_written: int = 0
    load_cleanup_duration_seconds: float = 0.0
    load_serialization_duration_seconds: float = 0.0
    load_bytes_by_category: Dict[str, int] = field(default_factory=dict)
    load_output_paths: List[str] = field(default_factory=list)
    load_output_paths_by_category: Dict[str, List[str]] = field(default_factory=dict)
    load_output_summary: Dict[str, Dict[str, any]] = field(default_factory=dict)

    # === Dropped record load metrics ===
    load_dropped_records_written: int = 0
    load_dropped_files_written: int = 0
    load_dropped_bytes_written: int = 0
    load_dropped_output_paths: List[str] = field(default_factory=list)

    def get_payload(self) -> Dict[str, Any]:
        """
        Return transform_images-specific metrics.

        This payload is indexed in the job-specific OpenSearch index
        for deep-dive analysis of transform_images runs.

        Note: Dict structures with dynamic keys are converted to arrays
        for OpenSearch aggregation compatibility. For example:
        - {"parserA": {"records": 10}} becomes [{"name": "parserA", "records": 10}]
        """
        return {
            "extract": {
                "partitions_requested": self.extract_partitions_requested,
                "partitions_found": self.extract_partitions_found,
                "partitions_empty": self.extract_partitions_empty,
                "corrupt_records": self.extract_corrupt_records,
                "null_eventtime": self.extract_null_eventtime,
                "null_data": self.extract_null_data,
                "records_after_filter": self.extract_records_after_filter,
                "min_event_time": self.extract_min_event_time,
                "max_event_time": self.extract_max_event_time,
                "event_time_range_hours": self.extract_event_time_range_hours,
            },
            "transform": {
                "records_input": self.transform_records_input,
                "records_output": self.transform_records_output,
                "decryption_failures": self.transform_decryption_failures,
                "null_critical_fields": self.transform_null_critical_fields,
                # Array format: [{"name": "parser", "records": N, "dropped": M}]
                "data_types": self._dict_to_array(self.transform_data_types, "name"),
            },
            "load": {
                "records_input": self.load_records_input,
                "partitions_written": self.load_partitions_written,
                "files_written": self.load_files_written,
                "cleanup_duration_seconds": self.load_cleanup_duration_seconds,
                "serialization_duration_seconds": self.load_serialization_duration_seconds,
                # Array format: [{"category": "nautilus", "bytes": N}]
                "bytes_by_category": self._dict_to_array(
                    self.load_bytes_by_category, "category", "bytes"
                ),
                # Array format: [{"category": "nautilus", "paths": [...]}]
                "output_paths_by_category": self._dict_to_array(
                    self.load_output_paths_by_category, "category", "paths"
                ),
                # Array format: [{"category": "nautilus", "file_count": N, "bytes": M, ...}]
                "output_summary": self._dict_to_array(self.load_output_summary, "category"),
            },
            "dropped_records": {
                "records_written": self.load_dropped_records_written,
                "files_written": self.load_dropped_files_written,
                "bytes_written": self.load_dropped_bytes_written,
                "output_paths": self.load_dropped_output_paths,
            },
        }

    def get_summary(self) -> str:
        """Generate human-readable summary report with transform_images details"""
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
            "EXTRACT PHASE:",
            f"  Duration: {self.extract_duration_seconds:.2f} seconds",
            f"  Partitions requested: {self.extract_partitions_requested}",
            f"  Partitions found: {self.extract_partitions_found}",
            f"  Partitions empty: {self.extract_partitions_empty}",
            f"  Records read: {self.records_read:,}",
            f"  Records after filtering: {self.extract_records_after_filter:,}",
            "",
            "TRANSFORM PHASE:",
            f"  Duration: {self.transform_duration_seconds:.2f} seconds",
            f"  Records input: {self.transform_records_input:,}",
            f"  Records output: {self.transform_records_output:,}",
        ]

        # Add per-data_type metrics from nested structure
        if self.transform_data_types:
            report.append("  By data type:")
            for data_type in sorted(self.transform_data_types.keys()):
                dt_metrics = self.transform_data_types[data_type]
                records = dt_metrics.get('records', 0)
                dropped = dt_metrics.get('dropped', 0)
                report.append(f"    - {data_type}: {records:,} records, {dropped:,} dropped")

        report.extend([
            "",
            "LOAD PHASE:",
            f"  Duration: {self.load_duration_seconds:.2f} seconds",
            f"    - Cleanup: {self.load_cleanup_duration_seconds:.2f} seconds",
            f"    - Serialization: {self.load_serialization_duration_seconds:.2f} seconds",
            f"  Records input: {self.load_records_input:,}",
            f"  Records written: {self.records_written:,}",
            f"  Output partitions: {self.load_partitions_written}",
            f"  Output files: {self.load_files_written}",
        ])

        # Add by-category output path counts
        if self.load_output_paths_by_category:
            report.append("  By category:")
            for category in sorted(self.load_output_paths_by_category.keys()):
                file_count = len(self.load_output_paths_by_category[category])
                report.append(f"    - {category}: {file_count} files")

        report.append("")

        if total_dropped > 0:
            report.extend([
                f"DROPPED RECORDS: {total_dropped:,}",
                "  Breakdown by reason:",
            ])
            for reason, count in sorted(self.drop_reasons.items(), key=lambda x: -x[1]):
                percentage = (count / self.records_read * 100) if self.records_read > 0 else 0
                report.append(f"    - {reason}: {count:,} ({percentage:.2f}%)")
            report.append("")

        # Add dropped record load metrics if any were written
        if self.load_dropped_records_written > 0:
            report.extend([
                "DROPPED RECORDS LOAD:",
                f"  Records written: {self.load_dropped_records_written:,}",
                f"  Files written: {self.load_dropped_files_written}",
                f"  Bytes written: {self.load_dropped_bytes_written:,} ({self.load_dropped_bytes_written / (1024**3):.2f} GB)",
                "",
            ])

        # Calculate success rate
        if self.records_read > 0:
            success_rate = (self.records_written / self.records_read) * 100
            report.extend([
                "SUCCESS RATE:",
                f"  {self.records_written:,} / {self.records_read:,} records processed ({success_rate:.2f}%)",
                f"",
            ])

        report.append(f"{'='*80}")

        return "\n".join(report)


# Backward compatibility alias
JobMetrics = TransformImagesJobMetrics
