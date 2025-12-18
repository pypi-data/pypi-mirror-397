"""
Service for managing filter_images manifests.

Handles:
- Reading/writing manifests to S3
- Finding the latest successful manifest for a day
- Managing the latest.json pointer
- Generating run IDs and manifest paths
"""
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from dwh.jobs.filter_images.manifest.manifest_models import FilterManifest

logger = logging.getLogger(__name__)


class ManifestService(ABC):
    """
    Abstract base class for manifest operations.

    Implementations handle the actual S3 I/O operations.
    """

    @abstractmethod
    def read_manifest(self, manifest_path: str) -> Optional[FilterManifest]:
        """
        Read a manifest from the given path.

        Args:
            manifest_path: Full path to the manifest file

        Returns:
            FilterManifest if found and valid, None otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def write_manifest(self, manifest: FilterManifest, manifest_path: str) -> None:
        """
        Write a manifest to the given path.

        Args:
            manifest: The manifest to write
            manifest_path: Full path to write to
        """
        raise NotImplementedError

    @abstractmethod
    def list_manifests(self, manifests_dir: str) -> List[str]:
        """
        List all manifest files in a directory.

        Args:
            manifests_dir: Directory containing manifests

        Returns:
            List of manifest file paths
        """
        raise NotImplementedError

    @abstractmethod
    def delete_path(self, path: str) -> None:
        """
        Delete a file or directory.

        Args:
            path: Path to delete
        """
        raise NotImplementedError

    def get_latest_manifest(
        self,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int
    ) -> Optional[FilterManifest]:
        """
        Get the latest successful manifest for a given day.

        First tries latest.json, then falls back to scanning all manifests.

        Args:
            base_path: Base path for filtered images (e.g., s3://bucket/filtered_images)
            tz_name: Timezone name (e.g., "pacific")
            year, month, day: Date components

        Returns:
            Latest successful FilterManifest, or None if no successful run exists
        """
        manifests_dir = self._get_manifests_dir(base_path, tz_name, year, month, day)
        latest_path = f"{manifests_dir}/latest.json"

        # Try latest.json first
        latest_manifest = self.read_manifest(latest_path)
        if latest_manifest and latest_manifest.status == "SUCCESS":
            logger.info(f"Found latest manifest via latest.json: {latest_manifest.run_id}")
            return latest_manifest

        # Fallback: scan all manifests and find most recent SUCCESS
        logger.info("latest.json not found or invalid, scanning all manifests...")
        return self._find_latest_successful_manifest(manifests_dir)

    def _find_latest_successful_manifest(self, manifests_dir: str) -> Optional[FilterManifest]:
        """
        Scan all manifests in a directory and return the most recent successful one.

        Args:
            manifests_dir: Directory containing manifests

        Returns:
            Most recent successful manifest, or None
        """
        manifest_files = self.list_manifests(manifests_dir)

        # Filter to only manifest-*.json files (not latest.json)
        manifest_files = [
            f for f in manifest_files
            if f.endswith('.json') and 'manifest-' in f and 'latest' not in f
        ]

        if not manifest_files:
            logger.info("No manifest files found")
            return None

        # Sort by filename (which contains timestamp) in descending order
        manifest_files.sort(reverse=True)

        # Find first successful manifest
        for manifest_path in manifest_files:
            manifest = self.read_manifest(manifest_path)
            if manifest and manifest.status == "SUCCESS":
                logger.info(f"Found latest successful manifest: {manifest.run_id}")
                return manifest

        logger.info("No successful manifests found")
        return None

    def save_manifest(
        self,
        manifest: FilterManifest,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int,
        update_latest: bool = True
    ) -> str:
        """
        Save a manifest and optionally update the latest.json pointer.

        Args:
            manifest: The manifest to save
            base_path: Base path for filtered images
            tz_name: Timezone name
            year, month, day: Date components
            update_latest: Whether to update latest.json (only on SUCCESS)

        Returns:
            Full path where manifest was written
        """
        manifests_dir = self._get_manifests_dir(base_path, tz_name, year, month, day)
        manifest_path = f"{manifests_dir}/manifest-{manifest.run_id}.json"

        # Write the manifest
        self.write_manifest(manifest, manifest_path)
        logger.info(f"Wrote manifest to {manifest_path}")

        # Update latest.json if successful
        if update_latest and manifest.status == "SUCCESS":
            latest_path = f"{manifests_dir}/latest.json"
            self.write_manifest(manifest, latest_path)
            logger.info(f"Updated latest.json to point to {manifest.run_id}")

        return manifest_path

    def generate_run_id(self) -> str:
        """
        Generate a unique run ID for a filter job.

        Format: filter-{ISO_TIMESTAMP}-{SHORT_UUID}
        Example: filter-20251124T003000Z-abc123
        """
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        short_uuid = uuid.uuid4().hex[:6]
        return f"filter-{timestamp}-{short_uuid}"

    def get_output_path(
        self,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int,
        run_id: str
    ) -> str:
        """
        Get the output path for a filter run.

        Args:
            base_path: Base path for filtered images
            tz_name: Timezone name
            year, month, day: Date components
            run_id: Run ID

        Returns:
            Full output path for this run's parquet files
        """
        return f"{base_path}/{tz_name}/year={year}/month={month:02d}/day={day:02d}/{run_id}"

    def get_latest_output_path(
        self,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int
    ) -> str:
        """
        Get the "latest" output path for external clients.

        This path always points to the most recent successful run's data.
        External clients can read from this consistent path without needing
        to know specific run IDs.

        Args:
            base_path: Base path for filtered images
            tz_name: Timezone name
            year, month, day: Date components

        Returns:
            Path to "latest" output directory
        """
        return f"{base_path}/{tz_name}/year={year}/month={month:02d}/day={day:02d}/latest"

    def _get_manifests_dir(
        self,
        base_path: str,
        tz_name: str,
        year: int,
        month: int,
        day: int
    ) -> str:
        """Get the directory path for manifests."""
        return f"{base_path}/{tz_name}/year={year}/month={month:02d}/day={day:02d}/_manifests"


class SparkManifestService(ManifestService):
    """
    ManifestService implementation using Spark for S3 operations.

    Uses the Spark session's Hadoop filesystem API for S3 access.
    """

    def __init__(self, spark):
        """
        Initialize with a Spark session.

        Args:
            spark: Active SparkSession with S3 access configured
        """
        self.spark = spark
        self._hadoop_conf = spark._jsc.hadoopConfiguration()

    def read_manifest(self, manifest_path: str) -> Optional[FilterManifest]:
        """Read a manifest from S3 using Spark's Hadoop FS."""
        try:
            # Use Spark to read the JSON file
            from py4j.java_gateway import java_import
            java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")
            java_import(self.spark._jvm, "java.io.BufferedReader")
            java_import(self.spark._jvm, "java.io.InputStreamReader")

            path = self.spark._jvm.Path(manifest_path)
            fs = path.getFileSystem(self._hadoop_conf)

            if not fs.exists(path):
                logger.debug(f"Manifest not found: {manifest_path}")
                return None

            # Read file content
            input_stream = fs.open(path)
            reader = self.spark._jvm.BufferedReader(
                self.spark._jvm.InputStreamReader(input_stream, "UTF-8")
            )

            lines = []
            line = reader.readLine()
            while line is not None:
                lines.append(line)
                line = reader.readLine()
            reader.close()

            json_content = "\n".join(lines)
            return FilterManifest.from_json(json_content)

        except Exception as e:
            logger.warning(f"Error reading manifest from {manifest_path}: {e}")
            return None

    def write_manifest(self, manifest: FilterManifest, manifest_path: str) -> None:
        """Write a manifest to S3 using Spark's Hadoop FS."""
        from py4j.java_gateway import java_import
        java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
        java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")
        java_import(self.spark._jvm, "java.io.BufferedWriter")
        java_import(self.spark._jvm, "java.io.OutputStreamWriter")

        path = self.spark._jvm.Path(manifest_path)
        fs = path.getFileSystem(self._hadoop_conf)

        # Write file content
        output_stream = fs.create(path, True)  # True = overwrite
        writer = self.spark._jvm.BufferedWriter(
            self.spark._jvm.OutputStreamWriter(output_stream, "UTF-8")
        )

        writer.write(manifest.to_json())
        writer.close()

    def list_manifests(self, manifests_dir: str) -> List[str]:
        """List all manifest files in an S3 directory."""
        try:
            from py4j.java_gateway import java_import
            java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
            java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")

            path = self.spark._jvm.Path(manifests_dir)
            fs = path.getFileSystem(self._hadoop_conf)

            if not fs.exists(path):
                return []

            file_statuses = fs.listStatus(path)
            manifest_paths = []

            for status in file_statuses:
                file_path = status.getPath().toString()
                if file_path.endswith('.json'):
                    manifest_paths.append(file_path)

            return manifest_paths

        except Exception as e:
            logger.warning(f"Error listing manifests in {manifests_dir}: {e}")
            return []

    def delete_path(self, path: str) -> None:
        """Delete a file or directory from S3."""
        from py4j.java_gateway import java_import
        java_import(self.spark._jvm, "org.apache.hadoop.fs.Path")
        java_import(self.spark._jvm, "org.apache.hadoop.fs.FileSystem")

        hadoop_path = self.spark._jvm.Path(path)
        fs = hadoop_path.getFileSystem(self._hadoop_conf)

        if fs.exists(hadoop_path):
            fs.delete(hadoop_path, True)  # True = recursive
            logger.info(f"Deleted: {path}")


class NoopManifestService(ManifestService):
    """
    Noop implementation for testing.

    Stores manifests in memory instead of S3.
    """

    def __init__(self):
        self._manifests: dict = {}  # path -> FilterManifest

    def read_manifest(self, manifest_path: str) -> Optional[FilterManifest]:
        """Read from in-memory store."""
        return self._manifests.get(manifest_path)

    def write_manifest(self, manifest: FilterManifest, manifest_path: str) -> None:
        """Write to in-memory store."""
        self._manifests[manifest_path] = manifest
        logger.info(f"NOOP: Wrote manifest to {manifest_path}")

    def list_manifests(self, manifests_dir: str) -> List[str]:
        """List manifests from in-memory store."""
        return [
            path for path in self._manifests.keys()
            if path.startswith(manifests_dir) and path.endswith('.json')
        ]

    def delete_path(self, path: str) -> None:
        """Delete from in-memory store."""
        keys_to_delete = [k for k in self._manifests.keys() if k.startswith(path)]
        for key in keys_to_delete:
            del self._manifests[key]
        logger.info(f"NOOP: Deleted {len(keys_to_delete)} items at {path}")
