#!/usr/bin/env python3
"""
Create pull requests in Azure DevOps.

This module provides functionality to create PRs with support for:
- YAML configuration files
- Git commit message extraction
- Interactive prompts for missing fields
- Dry-run mode
"""

import base64
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests
import typer
import yaml
from dotenv import load_dotenv
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm, Prompt
from rich.table import Table

from jps_ado_pr_utils.constants import DEFAULT_ENV_FILE, ORG
from jps_ado_pr_utils.logging_helper import setup_logging

# Setup logging
logger = logging.getLogger(__name__)

app = typer.Typer()
console = Console()


# ---------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------
class PullRequestData:
    """Data for creating a pull request."""
    
    def __init__(
        self,
        summary: str,
        source_branch: str,
        target_branch: str,
        reviewers: List[str],
        approvers: List[str],
        jira_id: Optional[str] = None,
        body: Optional[str] = None,
        changes: Optional[List[str]] = None,
    ):
        self.summary = summary
        self.source_branch = source_branch
        self.target_branch = target_branch
        self.reviewers = reviewers
        self.approvers = approvers
        self.jira_id = jira_id
        self.body = body
        self.changes = changes or []


# ---------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------
def load_env():
    """Load environment variables from .env file.
    
    Returns:
        Tuple of (pat, user, project) where project may be None
    """
    logger.info(f"Loading environment variables from {DEFAULT_ENV_FILE}")
    
    if DEFAULT_ENV_FILE.exists():
        load_dotenv(DEFAULT_ENV_FILE)
        logger.info(f"Loaded environment from {DEFAULT_ENV_FILE}")
    else:
        logger.warning(f"Environment file {DEFAULT_ENV_FILE} not found")

    pat = os.getenv("AZDO_PAT")
    user = os.getenv("AZDO_USER")
    project = os.getenv("AZDO_PROJECT")

    if not pat:
        logger.error("AZDO_PAT not set")
        raise RuntimeError(
            f"AZDO_PAT not set (expected in {DEFAULT_ENV_FILE})"
        )
    if not user:
        logger.error("AZDO_USER not set")
        raise RuntimeError(
            f"AZDO_USER not set (expected in {DEFAULT_ENV_FILE})"
        )
    
    logger.info(f"Authenticated as user: {user}")
    if project:
        logger.info(f"Default project from environment: {project}")
    
    return pat, user, project


def auth_header(pat: str) -> Dict[str, str]:
    """Create authentication header for Azure DevOps API."""
    token = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------
# Git integration
# ---------------------------------------------------------------------
def get_current_branch() -> str:
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get current branch: {e}")
        raise RuntimeError("Failed to get current git branch")


def get_current_repository() -> str:
    """Get the current git repository name from the remote URL."""
    try:
        # Get the remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
        )
        remote_url = result.stdout.strip()
        
        # Parse repository name from URL
        # Examples:
        # https://dev.azure.com/org/project/_git/repo-name
        # git@ssh.dev.azure.com:v3/org/project/repo-name
        if "_git/" in remote_url:
            repo_name = remote_url.split("/_git/")[-1].rstrip("/")
        elif remote_url.endswith(".git"):
            repo_name = remote_url.split("/")[-1].replace(".git", "")
        else:
            repo_name = remote_url.split("/")[-1]
        
        logger.info(f"Detected repository from git remote: {repo_name}")
        return repo_name
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get repository name: {e}")
        raise RuntimeError("Failed to get current git repository. Are you in a git repository?")


def get_merge_base(source_branch: str, target_branch: str) -> str:
    """Get the merge base (common ancestor) of two branches."""
    try:
        result = subprocess.run(
            ["git", "merge-base", target_branch, source_branch],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get merge base: {e}")
        raise RuntimeError(f"Failed to find common ancestor between {source_branch} and {target_branch}")


def get_commit_messages(source_branch: str, target_branch: str) -> List[str]:
    """Get commit messages from source branch that aren't in target branch."""
    try:
        # Get commits in source that aren't in target
        result = subprocess.run(
            ["git", "log", f"{target_branch}..{source_branch}", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True,
        )
        messages = [msg.strip() for msg in result.stdout.split("\n") if msg.strip()]
        logger.info(f"Found {len(messages)} commit messages in {source_branch} not in {target_branch}")
        return messages
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get commit messages: {e}")
        raise RuntimeError(f"Failed to get commit messages between {target_branch} and {source_branch}")


# ---------------------------------------------------------------------
# YAML file parsing
# ---------------------------------------------------------------------
def load_pr_data_from_yaml(yaml_file: Path) -> Dict:
    """Load PR data from YAML file."""
    logger.info(f"Loading PR data from YAML file: {yaml_file}")
    
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f) or {}
    
    logger.info(f"Loaded YAML data with keys: {list(data.keys())}")
    return data


# ---------------------------------------------------------------------
# User prompts
# ---------------------------------------------------------------------
def prompt_for_value(
    field_name: str,
    yaml_value: Optional[str] = None,
    cli_value: Optional[str] = None,
    default: Optional[str] = None,
    required: bool = True,
) -> Optional[str]:
    """Prompt user for a value if not provided via CLI or YAML."""
    # CLI takes precedence
    if cli_value:
        return cli_value
    
    # Then YAML
    if yaml_value:
        return yaml_value
    
    # Then prompt
    if required:
        value = Prompt.ask(f"Enter {field_name}", default=default or "")
        if not value and required:
            raise RuntimeError(f"{field_name} is required")
        return value
    else:
        return Prompt.ask(f"Enter {field_name} (optional)", default=default or "")


def prompt_for_list(
    field_name: str,
    yaml_value: Optional[List[str]] = None,
    cli_value: Optional[str] = None,
    required: bool = True,
) -> List[str]:
    """Prompt user for a comma-separated list if not provided."""
    # CLI takes precedence
    if cli_value:
        return [item.strip() for item in cli_value.split(",") if item.strip()]
    
    # Then YAML
    if yaml_value:
        return yaml_value if isinstance(yaml_value, list) else []
    
    # Then prompt
    value = Prompt.ask(f"Enter {field_name} (comma-separated)", default="")
    if not value and required:
        raise RuntimeError(f"{field_name} is required")
    return [item.strip() for item in value.split(",") if item.strip()]


# ---------------------------------------------------------------------
# Azure DevOps user lookup
# ---------------------------------------------------------------------
def get_user_id(pat: str, project: str, email_or_name: str) -> Optional[str]:
    """Get Azure DevOps user ID from email or display name."""
    logger.info(f"Looking up user ID for: {email_or_name}")
    
    url = f"https://dev.azure.com/{ORG}/{project}/_apis/graph/users"
    headers = auth_header(pat)
    
    try:
        resp = requests.get(url, headers=headers, params={"api-version": "7.1-preview.1"})
        
        if resp.status_code != 200:
            logger.warning(f"Failed to fetch users: {resp.status_code}")
            return None
        
        users = resp.json().get("value", [])
        
        # Search by email or display name
        for user in users:
            if email_or_name.lower() in user.get("principalName", "").lower() or \
               email_or_name.lower() in user.get("displayName", "").lower():
                user_id = user.get("descriptor")
                logger.info(f"Found user ID for {email_or_name}: {user_id}")
                return user_id
        
        logger.warning(f"User not found: {email_or_name}")
        return None
        
    except Exception as e:
        logger.error(f"Error looking up user {email_or_name}: {e}")
        return None


# ---------------------------------------------------------------------
# PR creation
# ---------------------------------------------------------------------
def create_pull_request(
    pat: str,
    project: str,
    repository: str,
    pr_data: PullRequestData,
) -> Dict:
    """Create a pull request in Azure DevOps."""
    logger.info(f"Creating PR in {project}/{repository}")
    
    url = f"https://dev.azure.com/{ORG}/{project}/_apis/git/repositories/{repository}/pullrequests"
    headers = auth_header(pat)
    
    # Build description from body and changes
    description_parts = []
    
    if pr_data.jira_id:
        description_parts.append(f"**Jira Issue:** {pr_data.jira_id}\n")
    
    if pr_data.body:
        description_parts.append(pr_data.body)
        description_parts.append("\n")
    
    if pr_data.changes:
        description_parts.append("## Changes\n")
        for change in pr_data.changes:
            description_parts.append(f"- {change}")
        description_parts.append("\n")
    
    description = "\n".join(description_parts)
    
    # Build reviewer list
    reviewers = []
    
    # Add required reviewers (approvers)
    for approver in pr_data.approvers:
        user_id = get_user_id(pat, project, approver)
        if user_id:
            reviewers.append({
                "id": user_id,
                "isRequired": True,
            })
    
    # Add optional reviewers
    for reviewer in pr_data.reviewers:
        user_id = get_user_id(pat, project, reviewer)
        if user_id:
            reviewers.append({
                "id": user_id,
                "isRequired": False,
            })
    
    # Build PR payload
    payload = {
        "sourceRefName": f"refs/heads/{pr_data.source_branch}",
        "targetRefName": f"refs/heads/{pr_data.target_branch}",
        "title": pr_data.summary,
        "description": description,
    }
    
    if reviewers:
        payload["reviewers"] = reviewers
    
    logger.info(f"PR payload: {payload}")
    
    # Create the PR
    resp = requests.post(
        url,
        headers=headers,
        json=payload,
        params={"api-version": "7.1"},
    )
    
    if resp.status_code not in (200, 201):
        logger.error(f"Failed to create PR: {resp.status_code}")
        logger.error(f"Response: {resp.text}")
        raise RuntimeError(
            f"Failed to create pull request\n"
            f"HTTP {resp.status_code}\n"
            f"{resp.text}"
        )
    
    result = resp.json()
    logger.info(f"Successfully created PR #{result.get('pullRequestId')}")
    return result


# ---------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------
def display_pr_summary(pr_data: PullRequestData, project: str, repository: str):
    """Display PR summary in a Rich table."""
    table = Table(title="Pull Request Summary", show_header=True, header_style="bold magenta")
    table.add_column("Field", style="cyan", width=20)
    table.add_column("Value", style="green")
    
    table.add_row("Project", project)
    table.add_row("Repository", repository)
    table.add_row("Summary", pr_data.summary)
    table.add_row("Source Branch", pr_data.source_branch)
    table.add_row("Target Branch", pr_data.target_branch)
    
    if pr_data.jira_id:
        table.add_row("Jira ID", pr_data.jira_id)
    
    if pr_data.reviewers:
        table.add_row("Reviewers", ", ".join(pr_data.reviewers))
    
    if pr_data.approvers:
        table.add_row("Approvers (Required)", ", ".join(pr_data.approvers))
    
    if pr_data.changes:
        changes_text = "\n".join(f"• {c}" for c in pr_data.changes)
        table.add_row("Changes", changes_text)
    
    if pr_data.body:
        table.add_row("Description", pr_data.body[:200] + ("..." if len(pr_data.body) > 200 else ""))
    
    console.print(table)


# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
@app.command()
def create(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Azure DevOps project name (defaults to AZDO_PROJECT from .env)",
    ),
    repository: Optional[str] = typer.Option(
        None,
        "--repository",
        help="Repository name (defaults to current git repository)",
    ),
    body_file: Optional[Path] = typer.Option(
        None,
        "--body-file",
        exists=True,
        readable=True,
        help="YAML file with PR details",
    ),
    summary: Optional[str] = typer.Option(
        None,
        "--summary",
        help="PR title/summary",
    ),
    source_branch: Optional[str] = typer.Option(
        None,
        "--source-branch",
        help="Source branch (defaults to current branch)",
    ),
    target_branch: Optional[str] = typer.Option(
        None,
        "--target-branch",
        help="Target branch (e.g., main, develop)",
    ),
    reviewers: Optional[str] = typer.Option(
        None,
        "--reviewers",
        help="Comma-separated list of reviewer emails or names",
    ),
    approvers: Optional[str] = typer.Option(
        None,
        "--approvers",
        help="Comma-separated list of required approver emails or names",
    ),
    jira_id: Optional[str] = typer.Option(
        None,
        "--jira-id",
        help="Jira issue identifier",
    ),
    dryrun: bool = typer.Option(
        False,
        "--dryrun",
        help="Show what would be created without actually creating the PR",
    ),
    outdir: Optional[Path] = typer.Option(
        None,
        "--outdir",
        help="Output directory for log files",
    ),
    logfile: Optional[str] = typer.Option(
        None,
        "--logfile",
        help="Log file name (default: create_pr.log)",
    ),
):
    """Create a pull request in Azure DevOps."""
    try:
        # Setup logging
        if outdir:
            log_path = outdir / (logfile or "create_pr.log")
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
            username = os.getenv("USER", "user")
            default_outdir = Path(f"/tmp/{username}/jps-ado-pr-utils/{timestamp}")
            log_path = default_outdir / (logfile or "create_pr.log")
        
        setup_logging(logfile=log_path)
        logger.info("Starting PR creation")
        
        # Load authentication
        pat, user, env_project = load_env()
        logger.info(f"Creating PR as user: {user}")
        
        # Determine project (CLI > env variable)
        if not project:
            project = env_project
        
        if not project:
            logger.error("No project specified")
            raise RuntimeError(
                "Project must be specified via --project argument or AZDO_PROJECT environment variable"
            )
        
        logger.info(f"Using project: {project}")
        
        # Load YAML data if provided
        yaml_data = {}
        if body_file:
            yaml_data = load_pr_data_from_yaml(body_file)
        
        # Get repository (CLI > current git repository)
        if not repository:
            repository = get_current_repository()
        
        # Get source branch (CLI > YAML > current branch)
        if not source_branch:
            source_branch = yaml_data.get("source-branch") or get_current_branch()
        
        # Gather all required information
        final_summary = prompt_for_value(
            "summary",
            yaml_value=yaml_data.get("summary"),
            cli_value=summary,
            required=True,
        )
        
        final_target_branch = prompt_for_value(
            "target branch",
            yaml_value=yaml_data.get("target-branch"),
            cli_value=target_branch,
            default="main",
            required=True,
        )
        
        final_reviewers = prompt_for_list(
            "reviewers",
            yaml_value=yaml_data.get("reviewers"),
            cli_value=reviewers,
            required=False,
        )
        
        final_approvers = prompt_for_list(
            "approvers (required reviewers)",
            yaml_value=yaml_data.get("approvers"),
            cli_value=approvers,
            required=False,
        )
        
        final_jira_id = prompt_for_value(
            "Jira ID",
            yaml_value=yaml_data.get("jira-id"),
            cli_value=jira_id,
            required=False,
        )
        
        # Get commit messages as changes if not provided in YAML
        changes = yaml_data.get("changes", [])
        if not changes:
            try:
                changes = get_commit_messages(source_branch, final_target_branch)
            except Exception as e:
                logger.warning(f"Could not get commit messages: {e}")
                changes = []
        
        # Build PR data
        pr_data = PullRequestData(
            summary=final_summary,
            source_branch=source_branch,
            target_branch=final_target_branch,
            reviewers=final_reviewers,
            approvers=final_approvers,
            jira_id=final_jira_id,
            body=yaml_data.get("body"),
            changes=changes,
        )
        
        # Display summary
        console.print("\n")
        display_pr_summary(pr_data, project, repository)
        console.print("\n")
        
        # Confirm or create
        if dryrun:
            rprint("[yellow]DRY RUN: PR would be created with the above details[/yellow]")
            return
        
        should_create = Confirm.ask("Create this pull request?", default=True)
        
        if not should_create:
            rprint("[yellow]PR creation cancelled[/yellow]")
            return
        
        # Create the PR
        result = create_pull_request(pat, project, repository, pr_data)
        
        # Display success
        pr_id = result.get("pullRequestId")
        pr_url = result.get("_links", {}).get("web", {}).get("href", "")
        
        rprint(f"\n[green]✓ Successfully created PR #{pr_id}[/green]")
        if pr_url:
            rprint(f"[blue]URL: {pr_url}[/blue]")
        
    except Exception as e:
        logger.error(f"Error creating PR: {e}", exc_info=True)
        rprint(f"[red]ERROR: {e}[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
