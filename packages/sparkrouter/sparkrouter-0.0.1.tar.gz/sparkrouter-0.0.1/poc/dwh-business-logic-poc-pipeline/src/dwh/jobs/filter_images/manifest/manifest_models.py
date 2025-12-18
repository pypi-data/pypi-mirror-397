"""
Data models for filter_images manifests.

These models define the structure of manifest files used to track
filter job runs, enabling recovery and lineage tracking.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


@dataclass
class ManifestTimeRange:
    """A time range with start and end timestamps."""
    start: str  # ISO timestamp (UTC)
    end: str    # ISO timestamp (UTC)

    def to_dict(self) -> Dict[str, str]:
        return {"start": self.start, "end": self.end}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ManifestTimeRange":
        return cls(start=data["start"], end=data["end"])


@dataclass
class ManifestGap:
    """A gap in time coverage."""
    start: str   # ISO timestamp (UTC)
    end: str     # ISO timestamp (UTC)
    reason: str  # Why this gap exists

    def to_dict(self) -> Dict[str, str]:
        return {"start": self.start, "end": self.end, "reason": self.reason}

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "ManifestGap":
        return cls(start=data["start"], end=data["end"], reason=data.get("reason", "unknown"))


@dataclass
class ManifestLineageEntry:
    """Tracks a single contributing run in the lineage."""
    run_id: str
    transform_run_id: str
    time_range: ManifestTimeRange
    records_contributed: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "run_id": self.run_id,
            "transform_run_id": self.transform_run_id,
            "time_range": self.time_range.to_dict(),
            "records_contributed": self.records_contributed
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ManifestLineageEntry":
        return cls(
            run_id=data["run_id"],
            transform_run_id=data["transform_run_id"],
            time_range=ManifestTimeRange.from_dict(data["time_range"]),
            records_contributed=data["records_contributed"]
        )


@dataclass
class FilterManifest:
    """
    Complete manifest for a filter_images job run.

    This manifest tracks everything needed for:
    - Recovery (status, previous_manifest, output paths)
    - Coverage tracking (cumulative_range, gaps)
    - Lineage (which transform runs contributed)
    """
    schema_version: str = "1.0"
    run_id: str = None
    status: str = "IN_PROGRESS"  # IN_PROGRESS, SUCCESS, FAILED

    # Timing
    created_at: str = None
    completed_at: str = None
    processing_duration_seconds: float = 0.0

    # Context
    timezone: str = None
    day: str = None
    day_start_utc: str = None

    # Trigger info
    triggered_by_job: str = None
    triggered_by_run_id: str = None
    transform_output_path: str = None

    # Coverage
    cumulative_range: Optional[ManifestTimeRange] = None
    this_run_added: Optional[ManifestTimeRange] = None
    gaps: List[ManifestGap] = field(default_factory=list)

    # Input
    previous_manifest: Optional[str] = None
    previous_output_path: Optional[str] = None
    previous_record_count: int = 0
    transform_record_count: int = 0

    # Output
    output_path: str = None
    latest_output_path: str = None  # Consistent path for external clients
    output_files: List[str] = field(default_factory=list)
    record_count: int = 0
    bytes_written: int = 0
    duplicates_removed: int = 0

    # Lineage
    lineage: List[ManifestLineageEntry] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary for JSON serialization."""
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "status": self.status,
            "timing": {
                "created_at": self.created_at,
                "completed_at": self.completed_at,
                "processing_duration_seconds": self.processing_duration_seconds
            },
            "context": {
                "timezone": self.timezone,
                "day": self.day,
                "day_start_utc": self.day_start_utc
            },
            "triggered_by": {
                "job_name": self.triggered_by_job,
                "job_run_id": self.triggered_by_run_id,
                "output_path": self.transform_output_path
            },
            "coverage": {
                "cumulative_range": self.cumulative_range.to_dict() if self.cumulative_range else None,
                "this_run_added": self.this_run_added.to_dict() if self.this_run_added else None,
                "gaps": [g.to_dict() for g in self.gaps]
            },
            "input": {
                "previous_manifest": self.previous_manifest,
                "previous_output_path": self.previous_output_path,
                "previous_record_count": self.previous_record_count,
                "transform_record_count": self.transform_record_count
            },
            "output": {
                "path": self.output_path,
                "latest_path": self.latest_output_path,
                "files": self.output_files,
                "record_count": self.record_count,
                "bytes_written": self.bytes_written,
                "duplicates_removed": self.duplicates_removed
            },
            "lineage": [entry.to_dict() for entry in self.lineage]
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert manifest to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilterManifest":
        """Create manifest from dictionary."""
        timing = data.get("timing", {})
        context = data.get("context", {})
        triggered_by = data.get("triggered_by", {})
        coverage = data.get("coverage", {})
        input_data = data.get("input", {})
        output = data.get("output", {})

        # Parse coverage ranges
        cumulative_range = None
        if coverage.get("cumulative_range"):
            cumulative_range = ManifestTimeRange.from_dict(coverage["cumulative_range"])

        this_run_added = None
        if coverage.get("this_run_added"):
            this_run_added = ManifestTimeRange.from_dict(coverage["this_run_added"])

        # Parse gaps
        gaps = [ManifestGap.from_dict(g) for g in coverage.get("gaps", [])]

        # Parse lineage
        lineage = [ManifestLineageEntry.from_dict(e) for e in data.get("lineage", [])]

        return cls(
            schema_version=data.get("schema_version", "1.0"),
            run_id=data.get("run_id"),
            status=data.get("status", "UNKNOWN"),
            created_at=timing.get("created_at"),
            completed_at=timing.get("completed_at"),
            processing_duration_seconds=timing.get("processing_duration_seconds", 0.0),
            timezone=context.get("timezone"),
            day=context.get("day"),
            day_start_utc=context.get("day_start_utc"),
            triggered_by_job=triggered_by.get("job_name"),
            triggered_by_run_id=triggered_by.get("job_run_id"),
            transform_output_path=triggered_by.get("output_path"),
            cumulative_range=cumulative_range,
            this_run_added=this_run_added,
            gaps=gaps,
            previous_manifest=input_data.get("previous_manifest"),
            previous_output_path=input_data.get("previous_output_path"),
            previous_record_count=input_data.get("previous_record_count", 0),
            transform_record_count=input_data.get("transform_record_count", 0),
            output_path=output.get("path"),
            latest_output_path=output.get("latest_path"),
            output_files=output.get("files", []),
            record_count=output.get("record_count", 0),
            bytes_written=output.get("bytes_written", 0),
            duplicates_removed=output.get("duplicates_removed", 0),
            lineage=lineage
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FilterManifest":
        """Create manifest from JSON string."""
        return cls.from_dict(json.loads(json_str))

    def mark_success(self, completed_at: str, duration_seconds: float) -> None:
        """Mark the manifest as successful."""
        self.status = "SUCCESS"
        self.completed_at = completed_at
        self.processing_duration_seconds = duration_seconds

    def mark_failed(self, completed_at: str, duration_seconds: float) -> None:
        """Mark the manifest as failed."""
        self.status = "FAILED"
        self.completed_at = completed_at
        self.processing_duration_seconds = duration_seconds
