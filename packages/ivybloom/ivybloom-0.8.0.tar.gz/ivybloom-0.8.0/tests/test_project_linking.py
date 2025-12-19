"""
Tests for project linking functionality.

Tests LocalProjectManifest, LocalProjectSync, and project commands.
"""

import json
import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from ivybloom_cli.utils.project_linking import (
    LocalProjectManifest,
    LocalProjectSync,
    SyncStatus,
    SyncType,
    SyncChange,
    SyncConflict,
    SyncResult,
)


class TestLocalProjectManifest:
    """Tests for LocalProjectManifest class."""

    def test_manifest_creation(self):
        """Test creating a manifest."""
        manifest = LocalProjectManifest(
            version="1.0.0",
            project_id="proj_123",
            project_name="Test Project",
            linked_at=datetime.now().isoformat(),
            linked_path="/home/user/project",
        )

        assert manifest.version == "1.0.0"
        assert manifest.project_id == "proj_123"
        assert manifest.sync_status == SyncStatus.NEW
        assert manifest.include_jobs is True
        assert manifest.include_artifacts is True

    def test_manifest_to_dict(self):
        """Test converting manifest to dictionary."""
        now = datetime.now().isoformat()
        manifest = LocalProjectManifest(
            version="1.0.0",
            project_id="proj_123",
            project_name="Test Project",
            linked_at=now,
            linked_path="/home/user/project",
        )

        data = manifest.to_dict()

        assert data["version"] == "1.0.0"
        assert data["project_id"] == "proj_123"
        assert data["project_name"] == "Test Project"

    def test_manifest_save_and_load(self, tmp_path):
        """Test saving and loading manifest."""
        manifest_dir = tmp_path / ".ivybloom"
        now = datetime.now().isoformat()

        # Create and save
        manifest = LocalProjectManifest(
            version="1.0.0",
            project_id="proj_123",
            project_name="Test Project",
            linked_at=now,
            linked_path=str(tmp_path),
        )

        manifest.save(manifest_dir)

        # Verify file exists
        manifest_file = manifest_dir / "manifest.json"
        assert manifest_file.exists()

        # Load and verify
        loaded = LocalProjectManifest.load(manifest_dir)
        assert loaded.project_id == "proj_123"
        assert loaded.project_name == "Test Project"

    def test_manifest_validation_success(self, tmp_path):
        """Test manifest validation with valid data."""
        data = {
            "version": "1.0.0",
            "project_id": "proj_123",
            "project_name": "Test",
            "linked_at": datetime.now().isoformat(),
            "linked_path": str(tmp_path),
        }

        is_valid, error = LocalProjectManifest.validate(data)
        assert is_valid is True
        assert error is None

    def test_manifest_validation_missing_field(self, tmp_path):
        """Test manifest validation with missing required field."""
        data = {
            "version": "1.0.0",
            "project_id": "proj_123",
            # Missing project_name
            "linked_at": datetime.now().isoformat(),
            "linked_path": str(tmp_path),
        }

        is_valid, error = LocalProjectManifest.validate(data)
        assert is_valid is False
        assert "project_name" in error

    def test_manifest_validation_invalid_path(self):
        """Test manifest validation with non-existent path."""
        data = {
            "version": "1.0.0",
            "project_id": "proj_123",
            "project_name": "Test",
            "linked_at": datetime.now().isoformat(),
            "linked_path": "/nonexistent/path",
        }

        is_valid, error = LocalProjectManifest.validate(data)
        assert is_valid is False
        assert "does not exist" in error

    def test_manifest_update_sync_metadata(self):
        """Test updating manifest with sync metadata."""
        manifest = LocalProjectManifest(
            version="1.0.0",
            project_id="proj_123",
            project_name="Test Project",
            linked_at=datetime.now().isoformat(),
            linked_path="/home/user/project",
        )

        manifest.update_sync_metadata(
            sync_type="pull",
            status=SyncStatus.SYNCED,
            local_hash="abc123",
            remote_hash="def456",
        )

        assert manifest.last_sync_type == "pull"
        assert manifest.sync_status == SyncStatus.SYNCED
        assert manifest.local_state_hash == "abc123"
        assert manifest.remote_state_hash == "def456"
        assert manifest.last_sync_time is not None

    def test_manifest_load_missing_file(self, tmp_path):
        """Test loading manifest when file doesn't exist."""
        manifest_dir = tmp_path / ".ivybloom"

        with pytest.raises(FileNotFoundError):
            LocalProjectManifest.load(manifest_dir)

    def test_manifest_load_invalid_json(self, tmp_path):
        """Test loading manifest with invalid JSON."""
        manifest_dir = tmp_path / ".ivybloom"
        manifest_dir.mkdir()

        manifest_file = manifest_dir / "manifest.json"
        manifest_file.write_text("{invalid json")

        with pytest.raises(ValueError):
            LocalProjectManifest.load(manifest_dir)


class TestSyncChange:
    """Tests for SyncChange class."""

    def test_sync_change_creation(self):
        """Test creating a sync change."""
        change = SyncChange(
            resource_type="job",
            resource_id="job_123",
            change_type="added",
        )

        assert change.resource_type == "job"
        assert change.resource_id == "job_123"
        assert change.change_type == "added"


class TestSyncConflict:
    """Tests for SyncConflict class."""

    def test_sync_conflict_creation(self):
        """Test creating a sync conflict."""
        conflict = SyncConflict(
            resource_type="artifact",
            resource_id="art_123",
            local_version={"version": 1},
            remote_version={"version": 2},
        )

        assert conflict.resource_type == "artifact"
        assert conflict.resource_id == "art_123"
        assert conflict.resolved is False


class TestSyncResult:
    """Tests for SyncResult class."""

    def test_sync_result_success(self):
        """Test creating successful sync result."""
        result = SyncResult(
            success=True,
            sync_type=SyncType.PULL,
            timestamp=datetime.now().isoformat(),
            stats={"jobs": 2, "artifacts": 5},
        )

        assert result.success is True
        assert "2 jobs" in result.summary
        assert "5 artifacts" in result.summary

    def test_sync_result_failure(self):
        """Test creating failed sync result."""
        result = SyncResult(
            success=False,
            sync_type=SyncType.PULL,
            timestamp=datetime.now().isoformat(),
            errors=["Network timeout"],
        )

        assert result.success is False
        assert "Network timeout" in result.summary

    def test_sync_result_no_changes(self):
        """Test sync result with no changes."""
        result = SyncResult(
            success=True,
            sync_type=SyncType.PULL,
            timestamp=datetime.now().isoformat(),
            stats={"jobs": 0, "artifacts": 0},
        )

        assert "no changes" in result.summary.lower()


class TestLocalProjectSync:
    """Tests for LocalProjectSync class."""

    @pytest.fixture
    def manifest(self, tmp_path):
        """Create a test manifest."""
        return LocalProjectManifest(
            version="1.0.0",
            project_id="proj_123",
            project_name="Test Project",
            linked_at=datetime.now().isoformat(),
            linked_path=str(tmp_path),
        )

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client."""
        return Mock()

    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        return Mock()

    @pytest.fixture
    def sync(self, manifest, mock_api_client, mock_config):
        """Create a sync instance."""
        return LocalProjectSync(manifest, mock_api_client, mock_config)

    def test_sync_creation(self, sync):
        """Test creating sync manager."""
        assert sync.manifest.project_id == "proj_123"
        assert sync.api_client is not None

    def test_get_local_state_empty(self, sync, tmp_path):
        """Test getting local state when cache is empty."""
        state = sync._get_local_state()

        assert "jobs" in state
        assert "artifacts" in state
        assert state["jobs"] == {}
        assert state["artifacts"] == {}

    def test_get_local_state_with_cache(self, sync, tmp_path):
        """Test getting local state with cache files."""
        # Create cache files
        cache_dir = tmp_path / ".ivybloom" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        jobs_cache = {"job_1": {"id": "job_1", "status": "completed"}}
        with open(cache_dir / "jobs.json", "w") as f:
            json.dump(jobs_cache, f)

        state = sync._get_local_state()

        assert state["jobs"] == jobs_cache

    def test_compare_states_added(self, sync):
        """Test comparing states with added items."""
        local = {"jobs": {}, "artifacts": {}, "metadata": {}}
        remote = {
            "jobs": {"job_1": {"id": "job_1"}},
            "artifacts": {},
            "metadata": {},
        }

        diff = sync._compare_states(local, remote)

        assert len(diff["added"]) == 1
        assert diff["added"][0]["type"] == "job"
        assert diff["added"][0]["id"] == "job_1"

    def test_compare_states_deleted(self, sync):
        """Test comparing states with deleted items."""
        local = {
            "jobs": {"job_1": {"id": "job_1"}},
            "artifacts": {},
            "metadata": {},
        }
        remote = {"jobs": {}, "artifacts": {}, "metadata": {}}

        diff = sync._compare_states(local, remote)

        assert len(diff["deleted"]) == 1
        assert diff["deleted"][0]["type"] == "job"

    def test_compare_states_modified(self, sync):
        """Test comparing states with modified items."""
        local = {
            "jobs": {"job_1": {"id": "job_1", "version": 1}},
            "artifacts": {},
            "metadata": {},
        }
        remote = {
            "jobs": {"job_1": {"id": "job_1", "version": 2}},
            "artifacts": {},
            "metadata": {},
        }

        diff = sync._compare_states(local, remote)

        assert len(diff["modified"]) == 1
        assert diff["modified"][0]["type"] == "job"

    def test_detect_conflicts(self, sync):
        """Test detecting conflicts."""
        diff = {
            "modified": [
                {
                    "type": "job",
                    "id": "job_1",
                    "local": {"version": 1},
                    "remote": {"version": 2},
                }
            ],
            "added": [],
            "deleted": [],
        }

        conflicts = sync._detect_conflicts(diff)

        assert len(conflicts) == 1
        assert conflicts[0].resource_id == "job_1"

    def test_diff_to_changes(self, sync):
        """Test converting diff to changes."""
        diff = {
            "added": [{"type": "job", "id": "job_1"}],
            "modified": [{"type": "artifact", "id": "art_1"}],
            "deleted": [{"type": "job", "id": "job_2"}],
        }

        changes = sync._diff_to_changes(diff)

        assert len(changes) == 3
        assert changes[0].change_type == "added"
        assert changes[1].change_type == "modified"
        assert changes[2].change_type == "deleted"

    def test_compute_stats(self, sync):
        """Test computing statistics from diff."""
        diff = {
            "added": [
                {"type": "job", "id": "job_1"},
                {"type": "artifact", "id": "art_1"},
            ],
            "modified": [{"type": "job", "id": "job_2"}],
            "deleted": [],
        }

        stats = sync._compute_stats(diff)

        assert stats["jobs"] == 2  # 1 added + 1 modified
        assert stats["artifacts"] == 1  # 1 added

    @pytest.mark.asyncio
    async def test_pull_success(self, sync, mock_api_client, tmp_path):
        """Test successful pull operation."""
        # Setup
        sync.manifest.linked_path = str(tmp_path)
        cache_dir = tmp_path / ".ivybloom" / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)

        mock_api_client.list_project_jobs = AsyncMock(return_value=[])
        mock_api_client.list_project_artifacts = AsyncMock(return_value=[])

        # Execute
        result = await sync.pull()

        # Verify
        assert result.success is True
        assert result.sync_type == SyncType.PULL
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_pull_with_error(self, sync, mock_api_client, tmp_path):
        """Test pull with error."""
        sync.manifest.linked_path = str(tmp_path)
        (tmp_path / ".ivybloom").mkdir(exist_ok=True)

        mock_api_client.list_project_jobs = AsyncMock(
            side_effect=Exception("Network error")
        )

        result = await sync.pull()

        assert result.success is True  # Partial success allowed
        assert result.timestamp is not None

    @pytest.mark.asyncio
    async def test_compute_diff(self, sync):
        """Test computing diff."""
        # Mock API responses
        sync.api_client.list_project_jobs = AsyncMock(
            return_value=[{"id": "job_1"}]
        )
        sync.api_client.list_project_artifacts = AsyncMock(return_value=[])

        diff = await sync.compute_diff()

        assert "added" in diff
        assert "modified" in diff
        assert "deleted" in diff


class TestProjectCommands:
    """Tests for project commands."""

    def test_projects_init_basic(self, tmp_path, runner):
        """Test basic project init command."""
        # This requires Click CLI testing setup
        # Implementation in separate integration tests
        pass

    def test_projects_pull_no_manifest(self, runner, tmp_path):
        """Test pull command when manifest doesn't exist."""
        # This requires Click CLI testing setup
        pass

    def test_projects_status_valid(self, tmp_path, runner):
        """Test status command with valid manifest."""
        # This requires Click CLI testing setup
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

