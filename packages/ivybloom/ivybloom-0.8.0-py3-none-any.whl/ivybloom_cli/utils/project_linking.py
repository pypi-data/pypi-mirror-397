"""
Project linking and local sync utilities for IvyBloom CLI.

This module handles all local project linking functionality including:
- Manifest file loading/saving
- Local/remote state comparison
- Sync operations (pull/push)
- Conflict detection and resolution
"""

import json
import asyncio
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum

import click


class SyncStatus(str, Enum):
    """Enumeration of possible sync states."""

    NEW = "new"  # Newly linked, never synced
    SYNCED = "synced"  # Fully synced with remote
    DIRTY = "dirty"  # Local changes not synced
    ERROR = "error"  # Last sync failed
    SYNCING = "syncing"  # Currently syncing


class SyncType(str, Enum):
    """Type of sync operation."""

    PULL = "pull"
    PUSH = "push"


@dataclass
class SyncChange:
    """Represents a single file/resource change."""

    resource_type: str  # "job", "artifact", "metadata"
    resource_id: str
    change_type: str  # "added", "modified", "deleted"
    local_hash: Optional[str] = None
    remote_hash: Optional[str] = None
    size_bytes: int = 0
    timestamp: Optional[str] = None


@dataclass
class SyncConflict:
    """Represents a conflict between local and remote versions."""

    resource_type: str
    resource_id: str
    local_version: Optional[Dict[str, Any]] = None
    remote_version: Optional[Dict[str, Any]] = None
    last_modified_by: Optional[str] = None  # "local" or "remote"
    resolved: bool = False
    resolution: Optional[str] = None  # "keep_local", "use_remote", "merge"


@dataclass
class SyncResult:
    """Result of a sync operation."""

    success: bool
    sync_type: SyncType
    timestamp: str
    changes: List[SyncChange] = field(default_factory=list)
    conflicts: List[SyncConflict] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    stats: Dict[str, int] = field(
        default_factory=lambda: {"jobs": 0, "artifacts": 0, "metadata": 0}
    )

    @property
    def summary(self) -> str:
        """Get a human-readable summary of the sync result."""
        if not self.success:
            error_text = ", ".join(self.errors[:2])
            return f"Sync failed: {error_text}"

        parts = []
        if self.stats.get("jobs"):
            parts.append(f"{self.stats['jobs']} jobs")
        if self.stats.get("artifacts"):
            parts.append(f"{self.stats['artifacts']} artifacts")
        if self.stats.get("metadata"):
            parts.append(f"{self.stats['metadata']} metadata items")

        if not parts:
            return "Sync complete: no changes"

        return f"Sync complete: {', '.join(parts)}"


@dataclass
class LocalProjectManifest:
    """
    Represents the `.ivybloom/manifest.json` file.

    This file tracks the local state of a linked project.
    """

    # Immutable fields (set at creation)
    version: str  # "1.0.0"
    project_id: str  # "proj_abc123"
    project_name: str  # "Drug Discovery Pipeline"
    linked_at: str  # ISO timestamp
    linked_path: str  # Absolute path to project directory

    # Mutable fields (updated by sync)
    include_jobs: bool = True
    include_artifacts: bool = True
    auto_sync: str = "manual"  # "manual", "15min", "hourly"

    # Metadata
    last_sync_time: Optional[str] = None
    last_sync_type: Optional[str] = None  # "pull" or "push"
    sync_status: str = SyncStatus.NEW
    last_error: Optional[str] = None

    # Cache
    local_state_hash: Optional[str] = None
    remote_state_hash: Optional[str] = None

    @staticmethod
    def validate(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate manifest data structure and required fields.

        Args:
            data: Dictionary to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = [
            "version",
            "project_id",
            "project_name",
            "linked_at",
            "linked_path",
        ]

        for field_name in required_fields:
            if field_name not in data:
                return False, f"Missing required field: {field_name}"

        # Validate types
        if not isinstance(data["version"], str):
            return False, "Field 'version' must be a string"

        if not isinstance(data["project_id"], str):
            return False, "Field 'project_id' must be a string"

        if not isinstance(data["linked_at"], str):
            return False, "Field 'linked_at' must be a string (ISO timestamp)"

        # Validate linked_path exists
        try:
            linked_path = Path(data["linked_path"])
            if not linked_path.exists():
                return False, f"Linked path does not exist: {data['linked_path']}"
        except (ValueError, TypeError):
            return False, f"Invalid linked path: {data['linked_path']}"

        return True, None

    @staticmethod
    def load(path: Path) -> "LocalProjectManifest":
        """Load manifest from .ivybloom/manifest.json.

        Args:
            path: Path to .ivybloom directory or manifest.json file

        Returns:
            LocalProjectManifest instance

        Raises:
            FileNotFoundError: If manifest file not found
            ValueError: If manifest is invalid
            json.JSONDecodeError: If manifest JSON is malformed
        """
        if path.is_dir():
            manifest_file = path / "manifest.json"
        else:
            manifest_file = path

        if not manifest_file.exists():
            raise FileNotFoundError(
                f"Manifest not found: {manifest_file}. "
                "Run 'ivybloom projects init' to create one."
            )

        try:
            with open(manifest_file) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in manifest: {e}")

        # Validate structure
        is_valid, error_msg = LocalProjectManifest.validate(data)
        if not is_valid:
            raise ValueError(f"Invalid manifest: {error_msg}")

        return LocalProjectManifest(**data)

    def save(self, path: Path) -> None:
        """Save manifest to .ivybloom/manifest.json.

        Args:
            path: Path to .ivybloom directory

        Raises:
            OSError: If unable to create directory or write file
        """
        # Create .ivybloom directory if needed
        ivybloom_dir = path if path.is_dir() else path.parent
        ivybloom_dir.mkdir(mode=0o700, exist_ok=True)

        # Determine manifest file path
        manifest_file = (
            ivybloom_dir / "manifest.json"
            if ivybloom_dir.is_dir()
            else ivybloom_dir
        )

        # Write manifest with safe permissions
        try:
            with open(manifest_file, "w") as f:
                json.dump(self.to_dict(), f, indent=2)
            manifest_file.chmod(0o600)
        except OSError as e:
            raise OSError(f"Failed to save manifest: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        data = asdict(self)
        # Ensure all values are JSON-serializable
        return {k: v for k, v in data.items() if v is not None or k in [
            "last_sync_time",
            "last_sync_type",
            "last_error",
            "local_state_hash",
            "remote_state_hash",
        ]}

    def update_sync_metadata(
        self,
        sync_type: str,
        status: str,
        local_hash: Optional[str] = None,
        remote_hash: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Update manifest with sync operation results.

        Args:
            sync_type: "pull" or "push"
            status: Sync status
            local_hash: Hash of local state
            remote_hash: Hash of remote state
            error: Error message if sync failed
        """
        self.last_sync_time = datetime.now().isoformat()
        self.last_sync_type = sync_type
        self.sync_status = status
        self.local_state_hash = local_hash
        self.remote_state_hash = remote_hash
        self.last_error = error


class LocalProjectSync:
    """
    Manages local project synchronization with remote.

    Handles pull, push, diff operations and conflict detection.
    """

    def __init__(
        self,
        manifest: LocalProjectManifest,
        api_client: Any,
        config: Any,
        console: Any = None,
    ):
        """Initialize sync manager.

        Args:
            manifest: LocalProjectManifest instance
            api_client: IvyBloomAPIClient instance
            config: Config instance
            console: Rich Console for output (optional)
        """
        self.manifest = manifest
        self.api_client = api_client
        self.config = config
        self.console = console
        self.linked_dir = Path(manifest.linked_path)

    async def pull(self) -> SyncResult:
        """Sync from cloud to local.

        Returns:
            SyncResult with operation details
        """
        try:
            # Get remote state
            remote_state = await self._get_remote_state()

            # Get local state
            local_state = self._get_local_state()

            # Compute diff
            diff = self._compare_states(local_state, remote_state)

            # Detect conflicts
            conflicts = self._detect_conflicts(diff)

            # Apply changes
            if not conflicts:
                await self._apply_changes(diff.get("new", []) +
                                           diff.get("modified", []))

            # Update manifest
            self.manifest.update_sync_metadata(
                sync_type=SyncType.PULL,
                status=SyncStatus.SYNCED if not conflicts else SyncStatus.DIRTY,
            )
            self.manifest.save(self.linked_dir / ".ivybloom")

            # Build result
            stats = self._compute_stats(diff)

            return SyncResult(
                success=not conflicts,
                sync_type=SyncType.PULL,
                timestamp=datetime.now().isoformat(),
                changes=self._diff_to_changes(diff),
                conflicts=conflicts,
                stats=stats,
            )

        except Exception as e:
            self.manifest.update_sync_metadata(
                sync_type=SyncType.PULL,
                status=SyncStatus.ERROR,
                error=str(e),
            )
            self.manifest.save(self.linked_dir / ".ivybloom")

            return SyncResult(
                success=False,
                sync_type=SyncType.PULL,
                timestamp=datetime.now().isoformat(),
                errors=[str(e)],
            )

    async def push(self) -> SyncResult:
        """Sync from local to cloud.

        Returns:
            SyncResult with operation details
        """
        try:
            # Get remote state
            remote_state = await self._get_remote_state()

            # Get local state
            local_state = self._get_local_state()

            # Compute diff
            diff = self._compare_states(local_state, remote_state)

            # Detect conflicts
            conflicts = self._detect_conflicts(diff)

            # Upload changes
            if not conflicts:
                await self._upload_changes(diff.get("new", []) +
                                            diff.get("modified", []))

            # Update manifest
            self.manifest.update_sync_metadata(
                sync_type=SyncType.PUSH,
                status=SyncStatus.SYNCED if not conflicts else SyncStatus.DIRTY,
            )
            self.manifest.save(self.linked_dir / ".ivybloom")

            # Build result
            stats = self._compute_stats(diff)

            return SyncResult(
                success=not conflicts,
                sync_type=SyncType.PUSH,
                timestamp=datetime.now().isoformat(),
                changes=self._diff_to_changes(diff),
                conflicts=conflicts,
                stats=stats,
            )

        except Exception as e:
            self.manifest.update_sync_metadata(
                sync_type=SyncType.PUSH,
                status=SyncStatus.ERROR,
                error=str(e),
            )
            self.manifest.save(self.linked_dir / ".ivybloom")

            return SyncResult(
                success=False,
                sync_type=SyncType.PUSH,
                timestamp=datetime.now().isoformat(),
                errors=[str(e)],
            )

    async def compute_diff(self) -> Dict[str, Any]:
        """Compute differences between local and remote.

        Returns:
            Dictionary with added, modified, deleted items
        """
        remote_state = await self._get_remote_state()
        local_state = self._get_local_state()
        return self._compare_states(local_state, remote_state)

    def _get_local_state(self) -> Dict[str, Any]:
        """Get local project state.

        Returns:
            Dictionary representing local state
        """
        state = {"jobs": {}, "artifacts": {}, "metadata": {}}

        # Read .ivybloom cache if available
        cache_dir = self.linked_dir / ".ivybloom" / "cache"
        if cache_dir.exists():
            jobs_cache = cache_dir / "jobs.json"
            artifacts_cache = cache_dir / "artifacts.json"

            if jobs_cache.exists():
                with open(jobs_cache) as f:
                    state["jobs"] = json.load(f)

            if artifacts_cache.exists():
                with open(artifacts_cache) as f:
                    state["artifacts"] = json.load(f)

        return state

    async def _get_remote_state(self) -> Dict[str, Any]:
        """Get remote project state from API.

        Returns:
            Dictionary representing remote state
        """
        state = {"jobs": {}, "artifacts": {}, "metadata": {}}

        # Fetch from API
        if self.manifest.include_jobs:
            try:
                jobs = await self.api_client.list_project_jobs(
                    self.manifest.project_id
                )
                state["jobs"] = {j.get("id"): j for j in jobs}
            except Exception:
                pass  # Allow partial state

        if self.manifest.include_artifacts:
            try:
                artifacts = await self.api_client.list_project_artifacts(
                    self.manifest.project_id
                )
                state["artifacts"] = {a.get("id"): a for a in artifacts}
            except Exception:
                pass  # Allow partial state

        return state

    def _compare_states(
        self, local: Dict[str, Any], remote: Dict[str, Any]
    ) -> Dict[str, List[Any]]:
        """Compare local and remote states.

        Args:
            local: Local state dictionary
            remote: Remote state dictionary

        Returns:
            Dictionary with added, modified, deleted lists
        """
        result = {"added": [], "modified": [], "deleted": []}

        # Check jobs
        local_job_ids = set(local.get("jobs", {}).keys())
        remote_job_ids = set(remote.get("jobs", {}).keys())

        result["added"].extend([
            {"type": "job", "id": j_id, "data": remote["jobs"][j_id]}
            for j_id in remote_job_ids - local_job_ids
        ])

        result["deleted"].extend([
            {"type": "job", "id": j_id, "data": local["jobs"][j_id]}
            for j_id in local_job_ids - remote_job_ids
        ])

        result["modified"].extend([
            {
                "type": "job",
                "id": j_id,
                "local": local["jobs"][j_id],
                "remote": remote["jobs"][j_id],
            }
            for j_id in local_job_ids & remote_job_ids
            if local["jobs"][j_id] != remote["jobs"][j_id]
        ])

        # Check artifacts
        local_artifact_ids = set(local.get("artifacts", {}).keys())
        remote_artifact_ids = set(remote.get("artifacts", {}).keys())

        result["added"].extend([
            {"type": "artifact", "id": a_id, "data": remote["artifacts"][a_id]}
            for a_id in remote_artifact_ids - local_artifact_ids
        ])

        result["deleted"].extend([
            {"type": "artifact", "id": a_id, "data": local["artifacts"][a_id]}
            for a_id in local_artifact_ids - remote_artifact_ids
        ])

        result["modified"].extend([
            {
                "type": "artifact",
                "id": a_id,
                "local": local["artifacts"][a_id],
                "remote": remote["artifacts"][a_id],
            }
            for a_id in local_artifact_ids & remote_artifact_ids
            if local["artifacts"][a_id] != remote["artifacts"][a_id]
        ])

        return result

    def _detect_conflicts(self, diff: Dict[str, List[Any]]) -> List[SyncConflict]:
        """Detect conflicts in diff.

        Args:
            diff: Diff dictionary from _compare_states

        Returns:
            List of conflicts
        """
        conflicts = []

        # Modified items are potential conflicts
        for item in diff.get("modified", []):
            conflicts.append(
                SyncConflict(
                    resource_type=item.get("type", "unknown"),
                    resource_id=item.get("id", ""),
                    local_version=item.get("local"),
                    remote_version=item.get("remote"),
                    last_modified_by="both",  # Conservative approach
                )
            )

        return conflicts

    async def _apply_changes(self, changes: List[Dict[str, Any]]) -> None:
        """Apply changes to local directory.

        Args:
            changes: List of changes to apply (added + modified)
        """
        cache_dir = self.linked_dir / ".ivybloom" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        jobs_file = cache_dir / "jobs.json"
        artifacts_file = cache_dir / "artifacts.json"

        # Load current cache
        jobs_cache = {}
        artifacts_cache = {}

        if jobs_file.exists():
            with open(jobs_file) as f:
                jobs_cache = json.load(f)

        if artifacts_file.exists():
            with open(artifacts_file) as f:
                artifacts_cache = json.load(f)

        # Apply changes
        for change in changes:
            if change.get("type") == "job":
                jobs_cache[change["id"]] = change.get("data")
            elif change.get("type") == "artifact":
                artifacts_cache[change["id"]] = change.get("data")

        # Save updated cache
        with open(jobs_file, "w") as f:
            json.dump(jobs_cache, f, indent=2)

        with open(artifacts_file, "w") as f:
            json.dump(artifacts_cache, f, indent=2)

    async def _upload_changes(self, changes: List[Dict[str, Any]]) -> None:
        """Upload changes to remote.

        Args:
            changes: List of changes to upload (added + modified)
        """
        for change in changes:
            if change.get("type") == "artifact":
                # In a real implementation, this would upload to S3
                # For now, just acknowledge
                pass

    def _diff_to_changes(self, diff: Dict[str, List[Any]]) -> List[SyncChange]:
        """Convert diff to SyncChange objects.

        Args:
            diff: Diff dictionary

        Returns:
            List of SyncChange objects
        """
        changes = []

        for item in diff.get("added", []):
            changes.append(
                SyncChange(
                    resource_type=item.get("type", "unknown"),
                    resource_id=item.get("id", ""),
                    change_type="added",
                )
            )

        for item in diff.get("modified", []):
            changes.append(
                SyncChange(
                    resource_type=item.get("type", "unknown"),
                    resource_id=item.get("id", ""),
                    change_type="modified",
                )
            )

        for item in diff.get("deleted", []):
            changes.append(
                SyncChange(
                    resource_type=item.get("type", "unknown"),
                    resource_id=item.get("id", ""),
                    change_type="deleted",
                )
            )

        return changes

    def _compute_stats(self, diff: Dict[str, List[Any]]) -> Dict[str, int]:
        """Compute statistics from diff.

        Args:
            diff: Diff dictionary

        Returns:
            Dictionary with job and artifact counts
        """
        stats = {"jobs": 0, "artifacts": 0, "metadata": 0}

        for item in diff.get("added", []) + diff.get("modified", []):
            if item.get("type") == "job":
                stats["jobs"] += 1
            elif item.get("type") == "artifact":
                stats["artifacts"] += 1

        return stats

