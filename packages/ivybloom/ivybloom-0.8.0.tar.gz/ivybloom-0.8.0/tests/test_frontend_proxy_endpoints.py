"""
Unit tests for frontend proxy endpoint paths compliance.

Verifies that all API client endpoints use the frontend proxy format
(without /api/cli prefix) as specified in CLI_TOOL_IMPLEMENTATION.md.
"""

from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from ivybloom_cli.client.api_client import IvyBloomAPIClient
from ivybloom_cli.utils.config import Config
from ivybloom_cli.utils.auth import AuthManager


@pytest.fixture
def mock_config() -> Config:
    """Provide mock Config object."""
    config = Config()
    config.set("api_url", "https://test.api/api/v1")
    config.set("frontend_url", "https://test.frontend/api/cli-proxy")
    return config


@pytest.fixture
def mock_auth_manager(mock_config: Config) -> AuthManager:
    """Provide mock AuthManager."""
    manager = AuthManager(mock_config)
    manager._cache_auth_token("test-token")
    return manager


@pytest.fixture
def mock_api_client(mock_config: Config, mock_auth_manager: AuthManager) -> IvyBloomAPIClient:
    """Provide mock API client."""
    return IvyBloomAPIClient(mock_config, mock_auth_manager)


class TestProjectEndpoints:
    """Test project endpoint paths."""

    def test_list_projects_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_projects uses /projects path (not /api/cli/projects)."""
        mock_response = [{"id": "proj-1", "name": "Test Project"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.list_projects()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/projects", f"Expected /projects, got {call_args[0]}"

    def test_get_project_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_project uses /projects/{id} path."""
        mock_response = {"id": "proj-1", "name": "Test Project"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_project("proj-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/projects/proj-1", f"Expected /projects/proj-1, got {call_args[0]}"

    def test_list_project_jobs_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_project_jobs uses /projects/{id}/jobs path."""
        mock_response = [{"id": "job-1", "status": "completed"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.list_project_jobs("proj-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert (
            call_args[0] == "/projects/proj-1/jobs"
        ), f"Expected /projects/proj-1/jobs, got {call_args[0]}"


class TestJobEndpoints:
    """Test job endpoint paths."""

    def test_create_job_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify create_job uses /jobs path."""
        mock_response = {"id": "job-1", "status": "pending"}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        job_request = {
            "tool_name": "test-tool",
            "parameters": {},
            "project_id": "proj-1",
        }
        mock_api_client.create_job(job_request)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/jobs", f"Expected /jobs, got {call_args[0]}"

    def test_get_job_status_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_job_status uses /jobs/{id} path."""
        mock_response = {"id": "job-1", "status": "completed", "progress_percent": 100}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_job_status("job-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/jobs/job-1", f"Expected /jobs/job-1, got {call_args[0]}"

    def test_get_job_results_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_job_results uses /jobs/{id}/results path."""
        mock_response = {"id": "job-1", "results": {"data": "test"}}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_job_results("job-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert (
            call_args[0] == "/jobs/job-1/results"
        ), f"Expected /jobs/job-1/results, got {call_args[0]}"

    def test_cancel_job_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify cancel_job uses /jobs/{id} path."""
        mock_response = {"success": True}
        mocker.patch.object(mock_api_client, "delete", return_value=mock_response)

        mock_api_client.cancel_job("job-1")

        mock_api_client.delete.assert_called_once()
        call_args = mock_api_client.delete.call_args[0]
        assert call_args[0] == "/jobs/job-1", f"Expected /jobs/job-1, got {call_args[0]}"

    def test_get_job_download_urls_uses_proxy_path(
        self, mock_api_client: IvyBloomAPIClient, mocker: Any
    ) -> None:
        """Verify get_job_download_urls uses /download path."""
        mock_response = {"download_urls": []}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_job_download_urls("job-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/download", f"Expected /download, got {call_args[0]}"

    def test_list_jobs_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_jobs uses /jobs path."""
        mock_response = [{"id": "job-1", "status": "completed"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.list_jobs()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/jobs", f"Expected /jobs, got {call_args[0]}"


class TestToolEndpoints:
    """Test tool endpoint paths."""

    def test_get_tools_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_tools uses /tools path."""
        mock_response = [{"name": "tool-1", "description": "Test Tool"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_tools()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/tools", f"Expected /tools, got {call_args[0]}"

    def test_get_tool_schema_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_tool_schema uses /tools/{name}/schema path."""
        mock_response = {"description": "Test Tool", "parameters": {}}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_tool_schema("test-tool")

        mock_api_client.get.assert_called()
        # First call should be to /tools/{name}/schema
        call_args = mock_api_client.get.call_args_list[0][0]
        assert call_args[0] == "/tools/test-tool/schema", f"Expected /tools/test-tool/schema, got {call_args[0]}"


class TestWorkflowEndpoints:
    """Test workflow endpoint paths."""

    def test_list_workflows_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_workflows uses /workflows path."""
        mock_response = [{"id": "wf-1", "name": "Test Workflow"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.list_workflows()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/workflows", f"Expected /workflows, got {call_args[0]}"

    def test_create_workflow_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify create_workflow uses /workflows path."""
        mock_response = {"id": "wf-1", "status": "created"}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        workflow_spec = {"name": "test", "steps": []}
        mock_api_client.create_workflow(workflow_spec)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/workflows", f"Expected /workflows, got {call_args[0]}"

    def test_get_workflow_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_workflow uses /workflows/{id} path."""
        mock_response = {"id": "wf-1", "name": "Test Workflow"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_workflow("wf-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/workflows/wf-1", f"Expected /workflows/wf-1, got {call_args[0]}"

    def test_execute_workflow_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify execute_workflow uses /workflows/{id}/execute path."""
        mock_response = {"id": "job-1", "status": "started"}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        mock_api_client.execute_workflow("wf-1", {"param": "value"})

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/workflows/wf-1/execute", f"Expected /workflows/wf-1/execute, got {call_args[0]}"


class TestDataEndpoints:
    """Test data file endpoint paths."""

    def test_list_data_files_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_data_files uses /data path."""
        mock_response = [{"id": "data-1", "name": "file.txt"}]
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.list_data_files()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/data", f"Expected /data, got {call_args[0]}"

    def test_upload_data_file_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify upload_data_file uses /data/upload path."""
        mock_response = {"id": "data-1", "status": "uploaded"}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        file_data = {"name": "file.txt", "data": "test"}
        mock_api_client.upload_data_file(file_data)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/data/upload", f"Expected /data/upload, got {call_args[0]}"

    def test_get_data_file_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_data_file uses /data/{id} path."""
        mock_response = {"id": "data-1", "name": "file.txt"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_data_file("data-1")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/data/data-1", f"Expected /data/data-1, got {call_args[0]}"

    def test_delete_data_file_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify delete_data_file uses /data/{id} path."""
        mock_response = {"success": True}
        mocker.patch.object(mock_api_client, "delete", return_value=mock_response)

        mock_api_client.delete_data_file("data-1")

        mock_api_client.delete.assert_called_once()
        call_args = mock_api_client.delete.call_args[0]
        assert call_args[0] == "/data/data-1", f"Expected /data/data-1, got {call_args[0]}"


class TestConfigEndpoints:
    """Test config endpoint paths."""

    def test_get_config_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_config uses /config path."""
        mock_response = {"setting1": "value1"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_config()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/config", f"Expected /config, got {call_args[0]}"

    def test_update_config_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify update_config uses /config path."""
        mock_response = {"success": True}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        settings = {"setting1": "new_value"}
        mock_api_client.update_config(settings)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/config", f"Expected /config, got {call_args[0]}"


class TestAccountEndpoints:
    """Test account endpoint paths."""

    def test_get_account_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_account uses /account path."""
        mock_response = {"id": "user-1", "email": "test@example.com"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_account()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/account", f"Expected /account, got {call_args[0]}"

    def test_get_usage_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_usage uses /usage path."""
        mock_response = {"jobs_run": 10, "storage_used": "1GB"}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.get_usage()

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/usage", f"Expected /usage, got {call_args[0]}"

    def test_check_cli_linking_status_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify check_cli_linking_status uses /link-status/{id} path."""
        mock_response = {"linked": True}
        mocker.patch.object(mock_api_client, "get", return_value=mock_response)

        mock_api_client.check_cli_linking_status("client-123")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args[0]
        assert call_args[0] == "/link-status/client-123", f"Expected /link-status/client-123, got {call_args[0]}"

    def test_verify_cli_linking_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify verify_cli_linking uses /verify-link/{id} path."""
        mock_response = {"linked": True}
        mocker.patch.object(mock_api_client, "post", return_value=mock_response)

        mock_api_client.verify_cli_linking("client-123")

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args[0]
        assert call_args[0] == "/verify-link/client-123", f"Expected /verify-link/client-123, got {call_args[0]}"


class TestReportEndpoints:
    """Test report endpoint paths."""

    def test_reports_post_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify reports_post uses /reports path."""
        mock_response = {"status": "processing"}
        mocker.patch.object(mock_api_client, "_make_request", return_value=MagicMock(status_code=200, json=lambda: mock_response))

        mock_api_client.reports_post("readiness", job_id="job-1")

        # Verify the correct path is used
        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/reports", f"Expected /reports, got {call_args[0][1]}"

    def test_reports_get_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify reports_get uses /reports path."""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"status": "ready"}
        mocker.patch.object(mock_api_client, "_make_request", return_value=mock_response_obj)

        mock_api_client.reports_get("readiness", job_id="job-1")

        # Verify the correct path is used
        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/reports", f"Expected /reports, got {call_args[0][1]}"


class TestExportEndpoints:
    """Test export endpoint paths."""

    def test_create_export_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify create_export uses /exports path."""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"id": "export-1"}
        mocker.patch.object(mock_api_client, "_make_request", return_value=mock_response_obj)

        spec = {"type": "csv"}
        mock_api_client.create_export(spec)

        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/exports", f"Expected /exports, got {call_args[0][1]}"

    def test_get_export_status_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_export_status uses /exports/{id} path."""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"status": "completed"}
        mocker.patch.object(mock_api_client, "_make_request", return_value=mock_response_obj)

        mock_api_client.get_export_status("export-1")

        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/exports/export-1", f"Expected /exports/export-1, got {call_args[0][1]}"

    def test_get_export_results_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify get_export_results uses /exports/{id}/results path."""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"data": []}
        mocker.patch.object(mock_api_client, "_make_request", return_value=mock_response_obj)

        mock_api_client.get_export_results("export-1")

        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/exports/export-1/results", f"Expected /exports/export-1/results, got {call_args[0][1]}"

    def test_list_export_catalog_uses_proxy_path(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify list_export_catalog uses /exports/catalog path."""
        mock_response_obj = MagicMock()
        mock_response_obj.status_code = 200
        mock_response_obj.json.return_value = {"catalogs": []}
        mocker.patch.object(mock_api_client, "_make_request", return_value=mock_response_obj)

        mock_api_client.list_export_catalog()

        call_args = mock_api_client._make_request.call_args
        assert call_args[0][1] == "/exports/catalog", f"Expected /exports/catalog, got {call_args[0][1]}"


class TestNoAPICliPrefix:
    """Test that no endpoints use /api/cli prefix."""

    def test_all_endpoints_exclude_api_cli_prefix(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify no endpoint paths contain /api/cli prefix."""
        # Mock all the HTTP methods
        mocker.patch.object(mock_api_client, "get", return_value={})
        mocker.patch.object(mock_api_client, "post", return_value={})
        mocker.patch.object(mock_api_client, "delete", return_value={})

        # Call various endpoints
        endpoints_to_test = [
            (mock_api_client.list_projects, []),
            (mock_api_client.get_project, ["proj-1"]),
            (mock_api_client.list_project_jobs, ["proj-1"]),
            (mock_api_client.list_jobs, []),
            (mock_api_client.get_job_status, ["job-1"]),
            (mock_api_client.get_job_results, ["job-1"]),
            (mock_api_client.cancel_job, ["job-1"]),
            (mock_api_client.get_tools, []),
            (mock_api_client.list_workflows, []),
            (mock_api_client.list_data_files, []),
            (mock_api_client.get_account, []),
            (mock_api_client.get_usage, []),
        ]

        for endpoint_method, args in endpoints_to_test:
            try:
                endpoint_method(*args)
            except Exception:
                # Some endpoints may fail due to mock setup, but we're checking paths
                pass

        # Check all calls to ensure no /api/cli prefix is used
        all_calls = (
            mock_api_client.get.call_args_list
            + mock_api_client.post.call_args_list
            + mock_api_client.delete.call_args_list
        )

        for call in all_calls:
            path = call[0][0] if call[0] else ""
            assert "/api/cli" not in path, f"Path {path} contains /api/cli prefix (should be removed)"


class TestHeadersAndAuth:
    """Test that headers are correctly set for proxy access."""

    def test_client_id_header_included(self, mock_api_client: IvyBloomAPIClient) -> None:
        """Verify x-ivybloom-client header is included."""
        headers = mock_api_client._get_default_headers()
        assert "x-ivybloom-client" in headers, "x-ivybloom-client header not found"
        assert headers["x-ivybloom-client"], "x-ivybloom-client header is empty"

    def test_trace_id_included_in_request(self, mock_api_client: IvyBloomAPIClient, mocker: Any) -> None:
        """Verify x-trace-id header is injected into requests."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}

        mocker.patch.object(mock_api_client.client, "request", return_value=mock_response)

        # Make a test request
        mock_api_client.get("/test")

        # Verify trace ID was included
        assert mock_api_client.client.request.called
        call_kwargs = mock_api_client.client.request.call_args[1]
        headers = call_kwargs.get("headers", {})
        assert "x-trace-id" in headers, "x-trace-id header not found in request"

