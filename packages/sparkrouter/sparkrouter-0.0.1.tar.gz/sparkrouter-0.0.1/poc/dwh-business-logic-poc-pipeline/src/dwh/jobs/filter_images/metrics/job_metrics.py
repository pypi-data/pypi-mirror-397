"""
Job metrics collector for filter_images job.

Extends AbstractJobMetrics with filter_images-specific metrics:
- Coverage tracking (cumulative time range, gaps)
- Deduplication stats
- Lineage tracking
- Manifest references
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from dwh.services.metrics.abstract_job_metrics import AbstractJobMetrics


@dataclass
class TimeRange:
    """Represents a time range with start and end."""
    start: str  # ISO timestamp
    end: str    # ISO timestamp


@dataclass
class Gap:
    """Represents a gap in coverage."""
    start: str   # ISO timestamp
    end: str     # ISO timestamp
    reason: str  # Why this gap exists


@dataclass
class LineageEntry:
    """Tracks which runs contributed to the current output."""
    run_id: str
    transform_run_id: str
    time_range_start: str
    time_range_end: str
    records_contributed: int


@dataclass
class FilterImagesJobMetrics(AbstractJobMetrics):
    """
    Metrics collector for FilterImagesJob.

    Inherits common fields from AbstractJobMetrics and adds
    filter_images-specific metrics in the payload.
    """

    # Override job_name default
    job_name: str = "filter_images"

    # === Context ===
    timezone: str = None  # e.g., "America/Los_Angeles"
    day: str = None       # e.g., "2025-11-24"
    day_start_utc: str = None  # Day start in UTC

    # === Trigger info ===
    triggered_by_job: str = None
    triggered_by_run_id: str = None
    transform_output_path: str = None

    # === Input metrics ===
    previous_manifest_path: Optional[str] = None
    previous_output_path: Optional[str] = None
    previous_record_count: int = 0
    transform_record_count: int = 0

    # === Coverage tracking ===
    cumulative_range_start: str = None
    cumulative_range_end: str = None
    this_run_range_start: str = None
    this_run_range_end: str = None
    coverage_gaps: List[Dict[str, str]] = field(default_factory=list)

    # === Deduplication metrics ===
    records_before_dedup: int = 0
    duplicates_removed: int = 0

    # === Output metrics ===
    output_path: str = None
    latest_output_path: str = None  # Consistent path for external clients
    output_files: List[str] = field(default_factory=list)

    # === Lineage tracking ===
    lineage: List[Dict[str, Any]] = field(default_factory=list)

    def add_gap(self, start: str, end: str, reason: str) -> None:
        """Add a coverage gap."""
        self.coverage_gaps.append({
            "start": start,
            "end": end,
            "reason": reason
        })

    def add_lineage_entry(
        self,
        run_id: str,
        transform_run_id: str,
        time_range_start: str,
        time_range_end: str,
        records_contributed: int
    ) -> None:
        """Add a lineage entry tracking source data."""
        self.lineage.append({
            "run_id": run_id,
            "transform_run_id": transform_run_id,
            "time_range": {
                "start": time_range_start,
                "end": time_range_end
            },
            "records_contributed": records_contributed
        })

    def get_payload(self) -> Dict[str, Any]:
        """
        Return filter_images-specific metrics.

        This payload is indexed in the job-specific OpenSearch index
        for deep-dive analysis of filter_images runs.
        """
        return {
            "context": {
                "timezone": self.timezone,
                "day": self.day,
                "day_start_utc": self.day_start_utc,
            },
            "triggered_by": {
                "job_name": self.triggered_by_job,
                "job_run_id": self.triggered_by_run_id,
                "output_path": self.transform_output_path,
            },
            "input": {
                "previous_manifest": self.previous_manifest_path,
                "previous_output_path": self.previous_output_path,
                "previous_record_count": self.previous_record_count,
                "transform_record_count": self.transform_record_count,
            },
            "coverage": {
                "cumulative_range": {
                    "start": self.cumulative_range_start,
                    "end": self.cumulative_range_end,
                } if self.cumulative_range_start else None,
                "this_run_added": {
                    "start": self.this_run_range_start,
                    "end": self.this_run_range_end,
                } if self.this_run_range_start else None,
                "gaps": self.coverage_gaps,
            },
            "deduplication": {
                "records_before_dedup": self.records_before_dedup,
                "duplicates_removed": self.duplicates_removed,
            },
            "output": {
                "path": self.output_path,
                "latest_path": self.latest_output_path,
                "files": self.output_files,
            },
            "lineage": self.lineage,
        }

    def get_summary(self) -> str:
        """Generate human-readable summary report with filter_images details."""
        duration = self.get_duration_seconds()

        report = [
            f"\n{'='*80}",
            f"JOB METRICS SUMMARY: {self.job_name}",
            f"{'='*80}",
            f"Job Run ID: {self.job_run_id or 'N/A'}",
            f"Status: {self.job_status or 'N/A'}",
            f"Platform: {self.service_provider or 'N/A'}",
            f"Environment: {self.environment or 'N/A'}",
            f"Total Duration: {duration:.2f} seconds",
            "",
            "CONTEXT:",
            f"  Timezone: {self.timezone or 'N/A'}",
            f"  Day: {self.day or 'N/A'}",
            f"  Triggered by: {self.triggered_by_job or 'N/A'} ({self.triggered_by_run_id or 'N/A'})",
            "",
            "INPUT:",
            f"  Previous filtered records: {self.previous_record_count:,}",
            f"  New transform records: {self.transform_record_count:,}",
            f"  Total before dedup: {self.records_before_dedup:,}",
            "",
            "DEDUPLICATION:",
            f"  Duplicates removed: {self.duplicates_removed:,}",
            f"  Records after dedup: {self.records_written:,}",
            "",
            "COVERAGE:",
            f"  Cumulative range: {self.cumulative_range_start or 'N/A'} to {self.cumulative_range_end or 'N/A'}",
            f"  This run added: {self.this_run_range_start or 'N/A'} to {self.this_run_range_end or 'N/A'}",
            f"  Gaps: {len(self.coverage_gaps)}",
        ]

        if self.coverage_gaps:
            for gap in self.coverage_gaps:
                report.append(f"    - {gap['start']} to {gap['end']}: {gap['reason']}")

        report.extend([
            "",
            "OUTPUT:",
            f"  Run Path: {self.output_path or 'N/A'}",
            f"  Latest Path: {self.latest_output_path or 'N/A'}",
            f"  Files written: {len(self.output_files)}",
            f"  Bytes written: {self.bytes_written:,}",
            "",
            "LINEAGE:",
            f"  Contributing runs: {len(self.lineage)}",
        ])

        for entry in self.lineage:
            time_range = entry.get('time_range', {})
            report.append(
                f"    - {entry['run_id']}: {entry['records_contributed']:,} records "
                f"({time_range.get('start', 'N/A')} to {time_range.get('end', 'N/A')})"
            )

        report.append(f"{'='*80}")

        return "\n".join(report)


# Backward compatibility alias
JobMetrics = FilterImagesJobMetrics
