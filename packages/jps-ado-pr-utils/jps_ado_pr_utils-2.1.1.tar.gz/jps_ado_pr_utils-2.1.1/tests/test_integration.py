#!/usr/bin/env python3
"""Integration tests for the jps-ado-pr-utils CLI."""
from __future__ import annotations

from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from jps_ado_pr_utils.list_open_prs import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_api_response():
    """Create a realistic Azure DevOps API response."""
    return {
        "value": [
            {
                "pullRequestId": 100,
                "title": "Feature: Add authentication",
                "creationDate": "2024-12-01T09:00:00Z",
                "createdBy": {
                    "displayName": "Alice Developer",
                    "uniqueName": "alice@example.com",
                },
                "repository": {"name": "backend-service"},
                "_links": {
                    "web": {
                        "href": "https://dev.azure.com/org/project/_git/backend/pullrequest/100"
                    }
                },
                "reviewers": [
                    {
                        "displayName": "Test User",
                        "uniqueName": "test.user@example.com",
                        "isRequired": True,
                        "vote": 0,
                    }
                ],
            },
            {
                "pullRequestId": 101,
                "title": "Fix: Database connection issue",
                "creationDate": "2024-12-10T14:30:00Z",
                "createdBy": {
                    "displayName": "Bob Builder",
                    "uniqueName": "bob@example.com",
                },
                "repository": {"name": "backend-service"},
                "_links": {
                    "web": {
                        "href": "https://dev.azure.com/org/project/_git/backend/pullrequest/101"
                    }
                },
                "reviewers": [
                    {
                        "displayName": "Test User",
                        "uniqueName": "test.user@example.com",
                        "isRequired": False,
                        "vote": 10,
                    }
                ],
            },
            {
                "pullRequestId": 102,
                "title": "Refactor: Clean up legacy code",
                "creationDate": "2024-12-15T10:00:00Z",
                "createdBy": {
                    "displayName": "Charlie Coder",
                    "uniqueName": "charlie@example.com",
                },
                "repository": {"name": "frontend-app"},
                "_links": {
                    "web": {
                        "href": "https://dev.azure.com/org/project/_git/frontend/pullrequest/102"
                    }
                },
                "reviewers": [],
            },
        ]
    }


class TestIntegrationActiveStatus:
    """Integration tests for active PR retrieval."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_active_prs_full_workflow(
        self, mock_load_env, mock_requests_get, runner, mock_api_response
    ):
        """Test complete workflow for listing active PRs."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject", "--status", "active"])

        assert result.exit_code == 0
        assert "TestProject" in result.stdout
        assert "Status filter: active" in result.stdout

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_mine_only_integration(
        self, mock_load_env, mock_requests_get, runner, mock_api_response
    ):
        """Test mine-only filter in full workflow."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject", "--mine-only"])

        assert result.exit_code == 0
        # Should show only PRs where test.user is a reviewer (2 out of 3)


class TestIntegrationClosedStatus:
    """Integration tests for closed PR retrieval."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_completed_prs(self, mock_load_env, mock_requests_get, runner):
        """Test listing completed (merged) PRs."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        completed_response = {
            "value": [
                {
                    "pullRequestId": 200,
                    "title": "Completed feature",
                    "creationDate": "2024-11-01T09:00:00Z",
                    "createdBy": {
                        "displayName": "Alice Developer",
                        "uniqueName": "alice@example.com",
                    },
                    "repository": {"name": "backend-service"},
                    "_links": {
                        "web": {
                            "href": "https://dev.azure.com/org/project/_git/backend/pullrequest/200"
                        }
                    },
                    "reviewers": [],
                }
            ]
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = completed_response
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject", "--status", "completed"])

        assert result.exit_code == 0
        assert "Status filter: completed" in result.stdout
        # Verify the API was called with correct status
        args, kwargs = mock_requests_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "completed"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_abandoned_prs(self, mock_load_env, mock_requests_get, runner):
        """Test listing abandoned PRs."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject", "--status", "abandoned"])

        assert result.exit_code == 0
        assert "Status filter: abandoned" in result.stdout
        args, kwargs = mock_requests_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "abandoned"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_all_prs(self, mock_load_env, mock_requests_get, runner):
        """Test listing all PRs regardless of status."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject", "--status", "all"])

        assert result.exit_code == 0
        assert "Status filter: all" in result.stdout
        args, kwargs = mock_requests_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "all"


class TestIntegrationMultiProject:
    """Integration tests for multiple projects."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_multiple_projects_different_statuses(
        self, mock_load_env, mock_requests_get, runner, mock_api_response
    ):
        """Test querying multiple projects with different PR counts."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(
            app, ["--project", "Project1,Project2,Project3", "--status", "completed"]
        )

        assert result.exit_code == 0
        # Should call API for each project
        assert mock_requests_get.call_count == 3


class TestIntegrationErrorHandling:
    """Integration tests for error scenarios."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_api_authentication_failure(self, mock_load_env, mock_requests_get, runner):
        """Test handling of authentication failures."""
        mock_load_env.return_value = ("bad_token", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.headers.get.return_value = "text/html"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject"])

        # The error is caught and displayed, so exit code is 0 but error is in output
        assert result.exit_code == 0
        assert "Error processing project" in result.stdout or "401" in str(result.exception)

    def test_missing_credentials(self, runner):
        """Test handling of missing environment variables."""
        with patch.dict("os.environ", {}, clear=True):
            result = runner.invoke(app, ["--project", "TestProject"])
            assert result.exit_code != 0


class TestIntegrationOutputFormatting:
    """Integration tests for output formatting."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_output_contains_pr_details(
        self, mock_load_env, mock_requests_get, runner, mock_api_response
    ):
        """Test that output contains expected PR details."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_api_response
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject"])

        assert result.exit_code == 0
        # Check for presence of table elements (though exact formatting may vary)
        assert "TestProject" in result.stdout

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_empty_results_handling(self, mock_load_env, mock_requests_get, runner):
        """Test output when no PRs are found."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_requests_get.return_value = mock_response

        result = runner.invoke(app, ["--project", "TestProject"])

        assert result.exit_code == 0
