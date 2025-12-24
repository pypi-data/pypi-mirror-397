#!/usr/bin/env python3
"""
Tests for PR creation functionality.
"""

import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import yaml
from typer.testing import CliRunner

from jps_ado_pr_utils.create_pr import (
    PullRequestData,
    auth_header,
    create_pull_request,
    get_commit_messages,
    get_current_branch,
    get_current_repository,
    get_merge_base,
    get_user_id,
    load_pr_data_from_yaml,
    app,
)

runner = CliRunner()


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def mock_env_vars(tmp_path):
    """Mock environment variables."""
    with patch.dict(
        os.environ, {
            "AZDO_PAT": "test_pat_token",
            "AZDO_USER": "test.user@example.com",
            "AZDO_PROJECT": "DefaultProject"
        }
    ):
        yield


@pytest.fixture
def sample_pr_data():
    """Sample PR data."""
    return PullRequestData(
        summary="Add new feature",
        source_branch="feature/new-feature",
        target_branch="main",
        reviewers=["reviewer1@example.com", "reviewer2@example.com"],
        approvers=["approver@example.com"],
        jira_id="PROJ-123",
        body="This is a test PR",
        changes=["Add feature A", "Update component B"],
    )


@pytest.fixture
def sample_yaml_file(tmp_path):
    """Create a sample YAML configuration file."""
    yaml_file = tmp_path / "pr_config.yaml"
    data = {
        "summary": "Test PR from YAML",
        "source-branch": "feature/yaml-test",
        "target-branch": "develop",
        "reviewers": ["user1@example.com", "user2@example.com"],
        "approvers": ["admin@example.com"],
        "jira-id": "TEST-456",
        "body": "PR body from YAML file",
        "changes": ["Change 1", "Change 2", "Change 3"],
    }
    with open(yaml_file, "w") as f:
        yaml.dump(data, f)
    return yaml_file


# ---------------------------------------------------------------------
# Test auth header
# ---------------------------------------------------------------------
class TestAuthHeader:
    """Test authentication header generation."""

    def test_auth_header_basic(self):
        """Test auth header creation."""
        import base64

        pat = "test_token"
        result = auth_header(pat)

        expected_token = base64.b64encode(f":{pat}".encode()).decode()

        assert result["Authorization"] == f"Basic {expected_token}"
        assert result["Accept"] == "application/json"
        assert result["Content-Type"] == "application/json"


# ---------------------------------------------------------------------
# Test Git integration
# ---------------------------------------------------------------------
class TestGitIntegration:
    """Test git-related functions."""

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_current_branch(self, mock_run):
        """Test getting current branch name."""
        mock_run.return_value = Mock(stdout="feature/test-branch\n", returncode=0)

        result = get_current_branch()

        assert result == "feature/test-branch"
        mock_run.assert_called_once()

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_current_branch_error(self, mock_run):
        """Test error handling when getting current branch."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "git")

        with pytest.raises(RuntimeError, match="Failed to get current git branch"):
            get_current_branch()

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_current_repository(self, mock_run):
        """Test getting current repository from git remote."""
        mock_run.return_value = Mock(
            stdout="https://dev.azure.com/org/project/_git/test-repo\n", returncode=0
        )

        result = get_current_repository()

        assert result == "test-repo"

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_current_repository_ssh_url(self, mock_run):
        """Test getting repository from SSH URL."""
        mock_run.return_value = Mock(stdout="git@ssh.dev.azure.com:v3/org/project/test-repo\n", returncode=0)

        result = get_current_repository()

        assert result == "test-repo"

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_current_repository_error(self, mock_run):
        """Test error when not in a git repository."""
        from subprocess import CalledProcessError

        mock_run.side_effect = CalledProcessError(1, "git")

        with pytest.raises(RuntimeError, match="Failed to get current git repository"):
            get_current_repository()

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_merge_base(self, mock_run):
        """Test getting merge base of two branches."""
        mock_run.return_value = Mock(stdout="abc123def456\n", returncode=0)

        result = get_merge_base("feature/test", "main")

        assert result == "abc123def456"

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_commit_messages(self, mock_run):
        """Test extracting commit messages."""
        commit_msgs = "feat: Add feature A\nfix: Fix bug B\ndocs: Update README"
        mock_run.return_value = Mock(stdout=commit_msgs, returncode=0)

        result = get_commit_messages("feature/test", "main")

        assert len(result) == 3
        assert "feat: Add feature A" in result
        assert "fix: Fix bug B" in result
        assert "docs: Update README" in result

    @patch("jps_ado_pr_utils.create_pr.subprocess.run")
    def test_get_commit_messages_empty(self, mock_run):
        """Test getting commit messages when there are none."""
        mock_run.return_value = Mock(stdout="", returncode=0)

        result = get_commit_messages("feature/test", "main")

        assert len(result) == 0


# ---------------------------------------------------------------------
# Test YAML loading
# ---------------------------------------------------------------------
class TestYamlLoading:
    """Test YAML file parsing."""

    def test_load_pr_data_from_yaml(self, sample_yaml_file):
        """Test loading PR data from YAML file."""
        data = load_pr_data_from_yaml(sample_yaml_file)

        assert data["summary"] == "Test PR from YAML"
        assert data["source-branch"] == "feature/yaml-test"
        assert data["target-branch"] == "develop"
        assert data["jira-id"] == "TEST-456"
        assert len(data["reviewers"]) == 2
        assert len(data["approvers"]) == 1
        assert len(data["changes"]) == 3

    def test_load_pr_data_from_empty_yaml(self, tmp_path):
        """Test loading from empty YAML file."""
        yaml_file = tmp_path / "empty.yaml"
        with open(yaml_file, "w") as f:
            f.write("")

        data = load_pr_data_from_yaml(yaml_file)

        assert data == {}


# ---------------------------------------------------------------------
# Test user lookup
# ---------------------------------------------------------------------
class TestUserLookup:
    """Test Azure DevOps user ID lookup."""

    @patch("jps_ado_pr_utils.create_pr.requests.get")
    def test_get_user_id_success(self, mock_get):
        """Test successful user ID lookup."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "principalName": "john.doe@example.com",
                    "displayName": "John Doe",
                    "descriptor": "user-123",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = get_user_id("test_pat", "TestProject", "john.doe@example.com")

        assert result == "user-123"

    @patch("jps_ado_pr_utils.create_pr.requests.get")
    def test_get_user_id_by_display_name(self, mock_get):
        """Test user lookup by display name."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "value": [
                {
                    "principalName": "john.doe@example.com",
                    "displayName": "John Doe",
                    "descriptor": "user-123",
                }
            ]
        }
        mock_get.return_value = mock_response

        result = get_user_id("test_pat", "TestProject", "John Doe")

        assert result == "user-123"

    @patch("jps_ado_pr_utils.create_pr.requests.get")
    def test_get_user_id_not_found(self, mock_get):
        """Test user not found."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"value": []}
        mock_get.return_value = mock_response

        result = get_user_id("test_pat", "TestProject", "nonexistent@example.com")

        assert result is None

    @patch("jps_ado_pr_utils.create_pr.requests.get")
    def test_get_user_id_api_error(self, mock_get):
        """Test handling API error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        result = get_user_id("bad_pat", "TestProject", "user@example.com")

        assert result is None


# ---------------------------------------------------------------------
# Test PR creation
# ---------------------------------------------------------------------
class TestPRCreation:
    """Test PR creation via Azure DevOps API."""

    @patch("jps_ado_pr_utils.create_pr.get_user_id")
    @patch("jps_ado_pr_utils.create_pr.requests.post")
    def test_create_pull_request_success(self, mock_post, mock_get_user_id, sample_pr_data):
        """Test successful PR creation."""
        # Mock user ID lookups
        mock_get_user_id.side_effect = ["reviewer1-id", "reviewer2-id", "approver-id"]

        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "pullRequestId": 12345,
            "title": "Add new feature",
            "_links": {"web": {"href": "https://dev.azure.com/org/project/_git/repo/pullrequest/12345"}},
        }
        mock_post.return_value = mock_response

        result = create_pull_request("test_pat", "TestProject", "test-repo", sample_pr_data)

        assert result["pullRequestId"] == 12345
        mock_post.assert_called_once()

        # Check the payload
        call_args = mock_post.call_args
        payload = call_args[1]["json"]

        assert payload["sourceRefName"] == "refs/heads/feature/new-feature"
        assert payload["targetRefName"] == "refs/heads/main"
        assert payload["title"] == "Add new feature"
        assert "PROJ-123" in payload["description"]
        assert len(payload["reviewers"]) == 3

    @patch("jps_ado_pr_utils.create_pr.get_user_id")
    @patch("jps_ado_pr_utils.create_pr.requests.post")
    def test_create_pull_request_api_error(self, mock_post, mock_get_user_id, sample_pr_data):
        """Test PR creation API error handling."""
        mock_get_user_id.return_value = "user-123"

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="Failed to create pull request"):
            create_pull_request("test_pat", "TestProject", "test-repo", sample_pr_data)


# ---------------------------------------------------------------------
# Test CLI
# ---------------------------------------------------------------------
class TestCLI:
    """Test CLI commands."""

    @patch("jps_ado_pr_utils.create_pr.create_pull_request")
    @patch("jps_ado_pr_utils.create_pr.get_commit_messages")
    @patch("jps_ado_pr_utils.create_pr.get_current_repository")
    @patch("jps_ado_pr_utils.create_pr.get_current_branch")
    @patch("jps_ado_pr_utils.create_pr.load_env")
    @patch("jps_ado_pr_utils.create_pr.Confirm.ask")
    def test_create_pr_with_all_cli_args(
        self, mock_confirm, mock_load_env, mock_current_branch, mock_current_repo, mock_commits, mock_create_pr
    ):
        """Test creating PR with all CLI arguments."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com", "DefaultProject")
        mock_current_branch.return_value = "feature/test"
        mock_current_repo.return_value = "test-repo"
        mock_commits.return_value = ["commit 1", "commit 2"]
        mock_confirm.return_value = True
        mock_create_pr.return_value = {
            "pullRequestId": 999,
            "_links": {"web": {"href": "https://example.com/pr/999"}},
        }

        result = runner.invoke(
            app,
            [
                "--project", "TestProject",
                "--repository", "test-repo",
                "--summary", "Test PR",
                "--source-branch", "feature/test",
                "--target-branch", "main",
                "--reviewers", "user1@example.com,user2@example.com",
                "--approvers", "admin@example.com",
                "--jira-id", "TEST-123",
            ],
        )

        assert result.exit_code == 0
        mock_create_pr.assert_called_once()

    @patch("jps_ado_pr_utils.create_pr.get_current_repository")
    @patch("jps_ado_pr_utils.create_pr.get_current_branch")
    @patch("jps_ado_pr_utils.create_pr.load_env")
    @patch("jps_ado_pr_utils.create_pr.load_pr_data_from_yaml")
    def test_create_pr_with_yaml_file(
        self, mock_load_yaml, mock_load_env, mock_current_branch, mock_current_repo, sample_yaml_file
    ):
        """Test creating PR with YAML configuration."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com", "DefaultProject")
        mock_current_branch.return_value = "feature/yaml-test"
        mock_current_repo.return_value = "test-repo"
        mock_load_yaml.return_value = {
            "summary": "Test from YAML",
            "target-branch": "develop",
            "reviewers": ["user@example.com"],
            "approvers": [],
        }

        # Use dryrun to avoid actual creation
        result = runner.invoke(
            app,
            [
                "--project", "TestProject",
                "--repository", "test-repo",
                "--body-file", str(sample_yaml_file),
                "--dryrun",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

    @patch("jps_ado_pr_utils.create_pr.get_current_repository")
    @patch("jps_ado_pr_utils.create_pr.get_current_branch")
    @patch("jps_ado_pr_utils.create_pr.load_env")
    def test_create_pr_dryrun(self, mock_load_env, mock_current_branch, mock_current_repo):
        """Test dryrun mode."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com", "DefaultProject")
        mock_current_branch.return_value = "feature/dryrun"
        mock_current_repo.return_value = "test-repo"

        result = runner.invoke(
            app,
            [
                "--project", "TestProject",
                "--repository", "test-repo",
                "--summary", "Dryrun test",
                "--target-branch", "main",
                "--dryrun",
            ],
        )

        assert result.exit_code == 0
        assert "DRY RUN" in result.stdout

    @patch("jps_ado_pr_utils.create_pr.get_current_repository")
    @patch("jps_ado_pr_utils.create_pr.get_current_branch")
    @patch("jps_ado_pr_utils.create_pr.load_env")
    def test_create_pr_project_from_env(self, mock_load_env, mock_current_branch, mock_current_repo):
        """Test project detection from AZDO_PROJECT environment variable."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com", "EnvProject")
        mock_current_branch.return_value = "feature/test"
        mock_current_repo.return_value = "test-repo"

        result = runner.invoke(
            app,
            [
                # No --project argument, should use env variable
                "--summary", "Test PR",
                "--target-branch", "main",
                "--dryrun",
            ],
        )

        assert result.exit_code == 0
        assert "EnvProject" in result.stdout or "DRY RUN" in result.stdout

    @patch("jps_ado_pr_utils.create_pr.load_env")
    def test_create_pr_no_project_error(self, mock_load_env):
        """Test error when no project is specified."""
        mock_load_env.return_value = ("test_pat", "test.user@example.com", None)

        result = runner.invoke(
            app,
            [
                "--summary", "Test PR",
                "--target-branch", "main",
            ],
        )

        assert result.exit_code == 1
        assert "Project must be specified" in result.stdout or result.exception is not None


# ---------------------------------------------------------------------
# Test PullRequestData model
# ---------------------------------------------------------------------
class TestPullRequestData:
    """Test PullRequestData class."""

    def test_pr_data_initialization(self):
        """Test PR data initialization."""
        pr_data = PullRequestData(
            summary="Test PR",
            source_branch="feature/test",
            target_branch="main",
            reviewers=["user1"],
            approvers=["user2"],
            jira_id="TEST-1",
            body="Test body",
            changes=["Change 1"],
        )

        assert pr_data.summary == "Test PR"
        assert pr_data.source_branch == "feature/test"
        assert pr_data.target_branch == "main"
        assert len(pr_data.reviewers) == 1
        assert len(pr_data.approvers) == 1
        assert pr_data.jira_id == "TEST-1"

    def test_pr_data_defaults(self):
        """Test PR data with optional fields."""
        pr_data = PullRequestData(
            summary="Test PR",
            source_branch="feature/test",
            target_branch="main",
            reviewers=[],
            approvers=[],
        )

        assert pr_data.jira_id is None
        assert pr_data.body is None
        assert pr_data.changes == []
