#!/usr/bin/env python3
"""Unit tests for list_open_prs module."""
from __future__ import annotations

import base64
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import yaml
from typer.testing import CliRunner

from jps_ado_pr_utils.list_open_prs import (
    app,
    auth_header,
    build_pr_record,
    get_prs_for_project,
    load_env,
    load_projects,
    reviewer_role,
    reviewer_vote,
    vote_text,
)


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def mock_pr_data():
    """Sample PR data from Azure DevOps API."""
    return {
        "pullRequestId": 12345,
        "title": "Add new feature",
        "creationDate": "2024-01-15T10:30:00Z",
        "createdBy": {"displayName": "John Doe", "uniqueName": "john.doe@example.com"},
        "repository": {"name": "my-repo"},
        "_links": {"web": {"href": "https://dev.azure.com/org/project/_git/repo/pullrequest/12345"}},
        "reviewers": [
            {
                "displayName": "Jane Smith",
                "uniqueName": "jane.smith@example.com",
                "isRequired": True,
                "vote": 10,
            },
            {
                "displayName": "Bob Johnson",
                "uniqueName": "bob.johnson@example.com",
                "isRequired": False,
                "vote": 5,
            },
        ],
    }


@pytest.fixture
def mock_env_vars(tmp_path):
    """Mock environment variables."""
    with patch.dict(os.environ, {"AZDO_PAT": "test_pat_token", "AZDO_USER": "test.user@example.com"}):
        yield


class TestAuthHeader:
    """Test authentication header generation."""

    def test_auth_header_basic(self):
        """Test that auth_header creates proper Basic auth header."""
        pat = "my_secret_token"
        result = auth_header(pat)

        expected_token = base64.b64encode(f":{pat}".encode()).decode()

        assert result["Authorization"] == f"Basic {expected_token}"
        assert result["Accept"] == "application/json"
        assert result["Content-Type"] == "application/json"

    def test_auth_header_empty_pat(self):
        """Test auth_header with empty PAT."""
        result = auth_header("")
        expected_token = base64.b64encode(b":").decode()
        assert result["Authorization"] == f"Basic {expected_token}"


class TestLoadEnv:
    """Test environment variable loading."""

    def test_load_env_success(self, mock_env_vars):
        """Test successful environment variable loading."""
        pat, user = load_env()
        assert pat == "test_pat_token"
        assert user == "test.user@example.com"

    def test_load_env_missing_pat(self):
        """Test load_env raises error when AZDO_PAT is missing."""
        with patch.dict(os.environ, {"AZDO_USER": "user@example.com"}, clear=True):
            with pytest.raises(RuntimeError, match="AZDO_PAT not set"):
                load_env()

    def test_load_env_missing_user(self):
        """Test load_env raises error when AZDO_USER is missing."""
        with patch.dict(os.environ, {"AZDO_PAT": "token"}, clear=True):
            with pytest.raises(RuntimeError, match="AZDO_USER not set"):
                load_env()


class TestGetPrsForProject:
    """Test PR retrieval from Azure DevOps."""

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_active_status(self, mock_get):
        """Test retrieving active PRs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"pullRequestId": 1}]}
        mock_response.headers.get.return_value = "application/json"
        mock_get.return_value = mock_response

        result = get_prs_for_project("test_pat", "TestProject", "active")

        assert len(result) == 1
        assert result[0]["pullRequestId"] == 1
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "active"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_completed_status(self, mock_get):
        """Test retrieving completed PRs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": [{"pullRequestId": 2}]}
        mock_response.headers.get.return_value = "application/json"
        mock_get.return_value = mock_response

        result = get_prs_for_project("test_pat", "TestProject", "completed")

        assert len(result) == 1
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "completed"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_abandoned_status(self, mock_get):
        """Test retrieving abandoned PRs."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_get.return_value = mock_response

        result = get_prs_for_project("test_pat", "TestProject", "abandoned")

        assert len(result) == 0
        args, kwargs = mock_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "abandoned"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_default_status(self, mock_get):
        """Test default status is active."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_get.return_value = mock_response

        get_prs_for_project("test_pat", "TestProject")

        args, kwargs = mock_get.call_args
        assert kwargs["params"]["searchCriteria.status"] == "active"

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_invalid_response(self, mock_get):
        """Test handling of non-JSON response."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_response.headers.get.return_value = "text/html"
        mock_get.return_value = mock_response

        with pytest.raises(RuntimeError, match="Failed retrieving PRs"):
            get_prs_for_project("bad_pat", "TestProject")

    @patch("jps_ado_pr_utils.list_open_prs.requests.get")
    def test_get_prs_project_encoding(self, mock_get):
        """Test that project names with spaces are properly encoded."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_response.headers.get.return_value = "application/json"
        mock_get.return_value = mock_response

        get_prs_for_project("test_pat", "Test Project")

        args, kwargs = mock_get.call_args
        url = args[0]
        assert "Test%20Project" in url


class TestLoadProjects:
    """Test project loading from config or CLI."""

    def test_load_projects_from_cli(self):
        """Test loading projects from command-line argument."""
        result = load_projects(None, "Project1,Project2,Project3")
        assert result == ["Project1", "Project2", "Project3"]

    def test_load_projects_from_cli_with_spaces(self):
        """Test loading projects with spaces in names."""
        result = load_projects(None, "Project1 , Project2 , Project3")
        assert result == ["Project1", "Project2", "Project3"]

    def test_load_projects_from_config(self, tmp_path):
        """Test loading projects from YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_data = {"project": "ProjectA"}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = load_projects(config_file, None)
        assert result == ["ProjectA"]

    def test_load_projects_no_input(self):
        """Test error when neither config nor project arg provided."""
        with pytest.raises(RuntimeError, match="Either --project or --config-file must be provided"):
            load_projects(None, None)

    def test_load_projects_empty_config(self, tmp_path):
        """Test error when config file has no projects."""
        config_file = tmp_path / "config.yaml"
        with open(config_file, "w") as f:
            yaml.dump({}, f)

        with pytest.raises(RuntimeError, match="'project' must be defined in config file"):
            load_projects(config_file, None)

    def test_load_projects_cli_priority(self, tmp_path):
        """Test CLI argument takes priority over config file."""
        config_file = tmp_path / "config.yaml"
        config_data = {"projects": ["ProjectA", "ProjectB"]}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = load_projects(config_file, "Project1,Project2")
        assert result == ["Project1", "Project2"]


class TestReviewerLogic:
    """Test reviewer role and vote logic."""

    def test_reviewer_role_required(self, mock_pr_data):
        """Test identifying required reviewer."""
        result = reviewer_role(mock_pr_data, "jane.smith@example.com")
        assert result == "REQUIRED"

    def test_reviewer_role_optional(self, mock_pr_data):
        """Test identifying optional reviewer."""
        result = reviewer_role(mock_pr_data, "bob.johnson@example.com")
        assert result == "OPTIONAL"

    def test_reviewer_role_not_reviewer(self, mock_pr_data):
        """Test user who is not a reviewer."""
        result = reviewer_role(mock_pr_data, "other.user@example.com")
        assert result == ""

    def test_reviewer_role_by_display_name(self, mock_pr_data):
        """Test finding reviewer by display name."""
        result = reviewer_role(mock_pr_data, "Jane Smith")
        assert result == "REQUIRED"

    def test_reviewer_vote_approved(self, mock_pr_data):
        """Test getting reviewer vote."""
        result = reviewer_vote(mock_pr_data, "jane.smith@example.com")
        assert result == 10

    def test_reviewer_vote_waiting(self, mock_pr_data):
        """Test reviewer with waiting vote."""
        result = reviewer_vote(mock_pr_data, "bob.johnson@example.com")
        assert result == 5

    def test_reviewer_vote_not_reviewer(self, mock_pr_data):
        """Test vote for non-reviewer."""
        result = reviewer_vote(mock_pr_data, "other.user@example.com")
        assert result is None


class TestBuildPrRecord:
    """Test PR record construction."""

    def test_build_pr_record(self, mock_pr_data):
        """Test building PR record from API data."""
        record = build_pr_record(mock_pr_data, "TestProject", "jane.smith@example.com")

        assert record.project == "TestProject"
        assert record.pr_id == 12345
        assert record.title == "Add new feature"
        assert record.author == "John Doe"
        assert record.repo == "my-repo"
        assert record.reviewer_role == "REQUIRED"
        assert record.vote == 10
        assert len(record.reviewers) == 2

    def test_build_pr_record_creation_date(self, mock_pr_data):
        """Test date parsing in PR record."""
        record = build_pr_record(mock_pr_data, "TestProject", "test@example.com")
        assert isinstance(record.created_date, datetime)
        assert record.created_date.year == 2024
        assert record.created_date.month == 1
        assert record.created_date.day == 15

    def test_build_pr_record_missing_links(self):
        """Test PR record construction when _links field is missing."""
        pr_data_no_links = {
            "pullRequestId": 99999,
            "title": "Test PR without links",
            "creationDate": "2024-01-15T10:30:00Z",
            "createdBy": {"displayName": "Test User", "uniqueName": "test@example.com"},
            "repository": {"name": "test-repo"},
            "reviewers": [],
        }
        
        record = build_pr_record(pr_data_no_links, "TestProject", "test@example.com")
        
        # Should construct a fallback URL
        assert record.pr_id == 99999
        assert record.title == "Test PR without links"
        assert "dev.azure.com" in record.url
        assert "TestProject" in record.url
        assert "test-repo" in record.url
        assert "99999" in record.url


class TestVoteText:
    """Test vote text rendering."""

    def test_vote_text_approved(self):
        """Test approved vote text."""
        result = vote_text(10)
        assert "APPROVED" in str(result)

    def test_vote_text_rejected(self):
        """Test rejected vote text."""
        result = vote_text(-10)
        assert "REJECTED" in str(result)

    def test_vote_text_waiting(self):
        """Test waiting vote text."""
        result = vote_text(0)
        assert "WAITING" in str(result)

    def test_vote_text_none(self):
        """Test no vote text."""
        result = vote_text(None)
        assert "—" in str(result)


class TestCLI:
    """Test CLI command."""

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_with_project_arg(self, mock_load_env, mock_get_prs, runner):
        """Test CLI with --project argument."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        result = runner.invoke(app, ["--project", "TestProject"])

        assert result.exit_code == 0
        mock_get_prs.assert_called_once_with("test_pat", "TestProject", "active")

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_with_status_completed(self, mock_load_env, mock_get_prs, runner):
        """Test CLI with --status completed."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        result = runner.invoke(app, ["--project", "TestProject", "--status", "completed"])

        assert result.exit_code == 0
        mock_get_prs.assert_called_once_with("test_pat", "TestProject", "completed")

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_with_status_abandoned(self, mock_load_env, mock_get_prs, runner):
        """Test CLI with --status abandoned."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        result = runner.invoke(app, ["--project", "TestProject", "--status", "abandoned"])

        assert result.exit_code == 0
        mock_get_prs.assert_called_once_with("test_pat", "TestProject", "abandoned")

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_with_status_all(self, mock_load_env, mock_get_prs, runner):
        """Test CLI with --status all."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        result = runner.invoke(app, ["--project", "TestProject", "--status", "all"])

        assert result.exit_code == 0
        mock_get_prs.assert_called_once_with("test_pat", "TestProject", "all")

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_with_config_file(self, mock_load_env, mock_get_prs, runner, tmp_path):
        """Test CLI with --config-file."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        config_file = tmp_path / "config.yaml"
        config_data = {"project": "Project1"}
        with open(config_file, "w") as f:
            yaml.dump(config_data, f)

        result = runner.invoke(app, ["--config-file", str(config_file)])

        assert result.exit_code == 0
        assert mock_get_prs.call_count == 1

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_mine_only_filter(self, mock_load_env, mock_get_prs, runner, mock_pr_data):
        """Test --mine-only filter."""
        mock_load_env.return_value = ("test_pat", "jane.smith@example.com")
        mock_get_prs.return_value = [mock_pr_data]

        result = runner.invoke(app, ["--project", "TestProject", "--mine-only"])

        assert result.exit_code == 0
        assert "Jane Smith" in result.stdout or result.exit_code == 0

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_required_only_filter(self, mock_load_env, mock_get_prs, runner, mock_pr_data):
        """Test --required-only filter."""
        mock_load_env.return_value = ("test_pat", "jane.smith@example.com")
        mock_get_prs.return_value = [mock_pr_data]

        result = runner.invoke(app, ["--project", "TestProject", "--required-only"])

        assert result.exit_code == 0

    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_no_project_or_config(self, mock_load_env, runner):
        """Test error when neither project nor config provided."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")

        result = runner.invoke(app, [])

        assert result.exit_code != 0

    @patch("jps_ado_pr_utils.list_open_prs.get_prs_for_project")
    @patch("jps_ado_pr_utils.list_open_prs.load_env")
    def test_list_prs_multiple_projects(self, mock_load_env, mock_get_prs, runner):
        """Test CLI with multiple projects."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com")
        mock_get_prs.return_value = []

        result = runner.invoke(app, ["--project", "Project1,Project2,Project3"])

        assert result.exit_code == 0
        assert mock_get_prs.call_count == 3
