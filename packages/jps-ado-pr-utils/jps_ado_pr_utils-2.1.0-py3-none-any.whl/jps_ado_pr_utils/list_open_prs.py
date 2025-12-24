#!/usr/bin/env python3
from __future__ import annotations


import os
import base64
import logging
import requests
import typer
import yaml

from collections import defaultdict

from typing import Dict, List
from pathlib import Path
from typing import Dict, List
from urllib.parse import quote
from datetime import datetime
from dataclasses import dataclass

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.text import Text

from .constants import ORG, API_VERSION, DEFAULT_ENV_FILE
from .logging_helper import setup_logging

# ---------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------
app = typer.Typer(help="List open Azure DevOps PRs across projects")
console = Console()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------
# Dataclass
# ---------------------------------------------------------------------
@dataclass
class PullRequestRecord:
    project: str
    pr_id: int
    title: str
    created_date: datetime
    author: str
    repo: str
    url: str
    reviewer_role: str
    vote: int | None
    reviewers: List[Dict]

# ---------------------------------------------------------------------
# Environment loading
# ---------------------------------------------------------------------
def load_env():
    logger.info(f"Loading environment variables from {DEFAULT_ENV_FILE}")
    
    if DEFAULT_ENV_FILE.exists():
        load_dotenv(DEFAULT_ENV_FILE)
        logger.info(f"Loaded environment from {DEFAULT_ENV_FILE}")
    else:
        logger.warning(f"Environment file {DEFAULT_ENV_FILE} not found")

    pat = os.getenv("AZDO_PAT")
    user = os.getenv("AZDO_USER")

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
    return pat, user

# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------
def auth_header(pat: str) -> Dict[str, str]:
    token = base64.b64encode(f":{pat}".encode()).decode()
    return {
        "Authorization": f"Basic {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

# ---------------------------------------------------------------------
# Azure DevOps helpers
# ---------------------------------------------------------------------
def get_prs_for_project(pat: str, project: str, status: str = "active") -> List[Dict]:
    logger.info(f"Fetching PRs for project '{project}' with status '{status}'")
    
    encoded_project = quote(project, safe="")
    url = f"https://dev.azure.com/{ORG}/{encoded_project}/_apis/git/pullrequests"
    params = {
        "searchCriteria.status": status,
        "api-version": API_VERSION,
    }
    
    logger.info(f"API URL: {url}")
    logger.debug(f"API params: {params}")

    resp = requests.get(url, headers=auth_header(pat), params=params)
    
    logger.info(f"API response status: {resp.status_code}")

    # Check for successful status code first
    if resp.status_code != 200:
        logger.error(f"API returned status {resp.status_code} for project '{project}'")
        logger.error(f"Response content-type: {resp.headers.get('content-type')}")
        logger.error(f"Response body: {resp.text[:1000]}")
        
        error_msg = f"Failed retrieving PRs for project '{project}'\n"
        error_msg += f"HTTP {resp.status_code}\n"
        
        if resp.status_code == 404:
            error_msg += f"Project '{project}' not found. Please check:\n"
            error_msg += f"  - Project name is correct (case-sensitive)\n"
            error_msg += f"  - Project exists in organization '{ORG}'\n"
            error_msg += f"  - You have access to the project\n"
        
        error_msg += f"\nResponse: {resp.text[:500]}"
        raise RuntimeError(error_msg)
    
    if "application/json" not in resp.headers.get("content-type", ""):
        logger.error(f"Invalid response content-type for project '{project}': {resp.headers.get('content-type')}")
        logger.error(f"Response body: {resp.text[:500]}")
        raise RuntimeError(
            f"Failed retrieving PRs for project '{project}'\n"
            f"HTTP {resp.status_code}\n"
            f"{resp.text[:500]}"
        )
    
    result = resp.json().get("value", [])
    logger.info(f"Retrieved {len(result)} PRs for project '{project}'")
    return result

# ---------------------------------------------------------------------
# Project loading
# ---------------------------------------------------------------------
def load_projects(config_file: Path | None, project_arg: str | None) -> List[str]:
    """Load projects from config or CLI.
    
    Returns a list of projects for backward compatibility.
    """
    if project_arg:
        projects = [p.strip() for p in project_arg.split(",") if p.strip()]
        logger.info(f"Loaded {len(projects)} projects from CLI argument: {projects}")
        return projects

    if not config_file:
        logger.error("No project or config file provided")
        raise RuntimeError("Either --project or --config-file must be provided")
    
    logger.info(f"Loading project from config file: {config_file}")

    with open(config_file, "r") as fh:
        data = yaml.safe_load(fh) or {}

    # Only accept single 'project' value
    project = data.get("project")
    if not project:
        logger.error(f"No 'project' found in config file: {config_file}")
        raise RuntimeError("'project' must be defined in config file as a single string value")
    
    if not isinstance(project, str):
        logger.error(f"'project' must be a string, not {type(project).__name__}")
        raise RuntimeError("'project' in config file must be a single string value, not a list")
    
    logger.info(f"Loaded project from config file: {project}")
    return [project]

def load_config_repositories(config_file: Path | None) -> List[str] | None:
    """Load repository filter from config file.
    
    Returns None if no repositories specified in config.
    """
    if not config_file:
        return None
    
    logger.info(f"Checking for repository filter in config file: {config_file}")
    
    with open(config_file, "r") as fh:
        data = yaml.safe_load(fh) or {}
    
    repos = data.get("repositories")
    if repos:
        if not isinstance(repos, list):
            logger.error("'repositories' must be a list")
            raise RuntimeError("'repositories' in config file must be a list")
        logger.info(f"Loaded {len(repos)} repositories from config file: {repos}")
        return repos
    
    logger.info("No repository filter in config file")
    return None

# ---------------------------------------------------------------------
# Repository loading
# ---------------------------------------------------------------------
def load_repositories(repos_arg: str | None) -> List[str] | None:
    """Load repository filter list from CLI argument.
    
    Returns None if no filter specified (show all repositories).
    """
    if not repos_arg:
        return None
    
    repos = [r.strip() for r in repos_arg.split(",") if r.strip()]
    logger.info(f"Filtering by {len(repos)} repositories: {repos}")
    return repos

# ---------------------------------------------------------------------
# Reviewer logic
# ---------------------------------------------------------------------
def reviewer_role(pr: Dict, user: str) -> str:
    for reviewer in pr.get("reviewers", []):
        if reviewer.get("uniqueName") == user or reviewer.get("displayName") == user:
            return "REQUIRED" if reviewer.get("isRequired") else "OPTIONAL"
    return ""



def reviewer_vote(pr: Dict, user: str) -> int | None:
    for reviewer in pr.get("reviewers", []):
        if reviewer.get("uniqueName") == user or reviewer.get("displayName") == user:
            return reviewer.get("vote")
    return None

# ---------------------------------------------------------------------
# Record construction
# ---------------------------------------------------------------------
def build_pr_record(pr: Dict, project: str, user: str) -> PullRequestRecord:
    created = datetime.fromisoformat(pr["creationDate"].replace("Z", "+00:00"))
    
    # Extract URL with fallback
    url = pr.get("_links", {}).get("web", {}).get("href", "")
    if not url:
        # Fallback: construct URL manually
        pr_id = pr.get("pullRequestId", "")
        repo_name = pr.get("repository", {}).get("name", "unknown")
        url = f"https://dev.azure.com/{ORG}/{quote(project, safe='')}/_git/{repo_name}/pullrequest/{pr_id}"
        logger.warning(f"PR {pr_id} missing _links field, using constructed URL: {url}")

    return PullRequestRecord(
        project=project,
        pr_id=pr["pullRequestId"],
        title=pr["title"],
        created_date=created,
        author=pr["createdBy"]["displayName"],
        repo=pr["repository"]["name"],
        url=url,
        reviewer_role=reviewer_role(pr, user),
        vote=reviewer_vote(pr, user),
        reviewers=pr.get("reviewers", []),
    )

# ---------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------
@app.command()
def list_prs(
    config_file: Path = typer.Option(
        None,
        "--config-file",
        exists=True,
        readable=True,
        help="YAML file with Azure DevOps project(s) and optional repositories",
    ),
    project: str = typer.Option(
        None,
        "--project",
        help="Azure DevOps project name (e.g., 'Baylor Genetics')",
    ),
    repos: str = typer.Option(
        None,
        "--repos",
        help="Comma-separated list of repository names to filter (e.g., 'repo1,repo2')",
    ),
    mine_only: bool = typer.Option(
        False,
        "--mine-only",
        help="Only show PRs where you are a reviewer",
    ),
    required_only: bool = typer.Option(
        False,
        "--required-only",
        help="Only show PRs where you are a REQUIRED reviewer (blocking PRs)",
    ),
    status: str = typer.Option(
        "active",
        "--status",
        help="PR status filter: 'active', 'completed', 'abandoned', 'all'",
    ),
    outdir: Path = typer.Option(
        None,
        "--outdir",
        help="Output directory for logs (default: /tmp/[user]/jps-ado-pr-utils/[timestamp])",
    ),
    logfile: Path = typer.Option(
        None,
        "--logfile",
        help="Log file path (default: [outdir]/list_prs.log)",
    ),
):
    """
    List PRs across one or more Azure DevOps projects.
    
    Note: In Azure DevOps, a 'project' is the top-level container (e.g., 'Baylor Genetics'),
    and 'repositories' are the git repos within that project (e.g., 'pipeline-nextflow-cancer').
    """
    # Setup default outdir and logfile if not provided
    if outdir is None:
        from datetime import datetime
        username = os.getenv("USER", "unknown")
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        outdir = Path(f"/tmp/{username}/jps-ado-pr-utils/{timestamp}")
    
    if logfile is None:
        logfile = outdir / "list_prs.log"
    
    # Setup logging
    setup_logging(logfile)
    
    logger.info("="*80)
    logger.info("Starting jps-ado-pr-utils")
    logger.info(f"Output directory: {outdir}")
    logger.info(f"Log file: {logfile}")
    logger.info(f"Status filter: {status}")
    logger.info(f"Mine only: {mine_only}")
    logger.info(f"Required only: {required_only}")
    
    pat, user = load_env()
    projects = load_projects(config_file, project)
    
    # Merge repository filters from CLI and config
    repo_filter_cli = load_repositories(repos)
    repo_filter_config = load_config_repositories(config_file) if config_file else None
    
    # CLI --repos takes precedence over config file repositories
    repo_filter = repo_filter_cli or repo_filter_config

    console.print(f"[bold]Authenticated reviewer:[/bold] {user}")
    console.print(f"[bold]Projects:[/bold] {', '.join(projects)}")
    console.print(f"[bold]Status filter:[/bold] {status}")
    if repo_filter:
        console.print(f"[bold]Repository filter:[/bold] {', '.join(repo_filter)}")
    console.print(f"[bold]Log file:[/bold] {logfile}\n")
    
    logger.info(f"Authenticated as: {user}")
    logger.info(f"Processing {len(projects)} projects")
    if repo_filter:
        logger.info(f"Filtering by repositories: {repo_filter}")

    records: List[PullRequestRecord] = []

    for proj in projects:
        logger.info(f"Processing project: {proj}")
        try:
            raw_prs = get_prs_for_project(pat, proj, status)
            logger.info(f"Found {len(raw_prs)} PRs in project '{proj}'")
            
            for pr in raw_prs:
                repo_name = pr["repository"]["name"]
                
                # Apply repository filter if specified
                if repo_filter and repo_name not in repo_filter:
                    logger.debug(f"Skipping PR #{pr['pullRequestId']} from repo '{repo_name}' (not in filter)")
                    continue
                
                record = build_pr_record(pr, proj, user)
                records.append(record)
                logger.debug(f"Added PR #{record.pr_id} from repo '{repo_name}': {record.title}")
        except Exception as e:
            logger.error(f"Error processing project '{proj}': {e}", exc_info=True)
            console.print(f"[red]Error processing project '{proj}': {e}[/red]")
            continue
    
    logger.info(f"Total PRs retrieved: {len(records)}")

    if required_only:
        logger.info(f"Applying required-only filter")
        before_count = len(records)
        records = [
            r for r in records
            if r.reviewer_role == "REQUIRED"
        ]
        logger.info(f"Filtered from {before_count} to {len(records)} PRs (required reviewers only)")
    elif mine_only:
        logger.info(f"Applying mine-only filter")
        before_count = len(records)
        records = [
            r for r in records
            if r.reviewer_role in ("REQUIRED", "OPTIONAL")
        ]
        logger.info(f"Filtered from {before_count} to {len(records)} PRs (my reviews only)")

    logger.info(f"Rendering {len(records)} PRs")
    render_pr_tables_by_project(records, status)
    logger.info("Completed successfully")
    logger.info("="*80)

# ---------------------------------------------------------------------
# Rich table output
# ---------------------------------------------------------------------
def render_pr_tables_by_project(records: List[PullRequestRecord], status: str = "active"):
    """
    Render one Rich table per project, sorting PRs by age (oldest first).
    """
    logger.info(f"Rendering tables for {len(records)} PRs")
    
    grouped: Dict[str, List[PullRequestRecord]] = defaultdict(list)

    for record in records:
        grouped[record.project].append(record)
    
    logger.info(f"PRs grouped into {len(grouped)} projects")

    status_label = "open" if status == "active" else status

    for project, project_records in sorted(grouped.items()):
        logger.info(f"Rendering table for project '{project}' with {len(project_records)} PRs")
        # 🔹 Sort by oldest PR first (review debt)
        project_records = sorted(
            project_records,
            key=lambda r: r.created_date
        )

        table = Table(
            title=f"📦 Project: {project} ({len(project_records)} {status_label} PRs)",
            header_style="bold cyan",
        )

        table.add_column("PR #", justify="right", style="bold")
        table.add_column("Created", style="yellow")
        table.add_column("Author")
        table.add_column("Codebase", style="magenta")
        table.add_column("Reviewer Role", justify="center")
        table.add_column("Vote", justify="center")
        table.add_column("Title")
        table.add_column("URL", style="blue")

        for r in project_records:
            role_text = (
                Text("REQUIRED", style="bold red")
                if r.reviewer_role == "REQUIRED"
                else Text("OPTIONAL", style="yellow")
                if r.reviewer_role == "OPTIONAL"
                else Text("—", style="dim")
            )

            table.add_row(
                str(r.pr_id),
                r.created_date.strftime("%Y-%m-%d"),
                r.author,
                r.repo,
                role_text,
                vote_text(r.vote),
                r.title,
                Text(r.url, style="link " + r.url),
            )

        console.print(table)
        console.print()


def vote_text(vote: int | None) -> Text:
    if vote is None:
        return Text("—", style="dim")
    if vote >= 5:
        return Text("APPROVED", style="bold green")
    if vote <= -10:
        return Text("REJECTED", style="bold red")
    return Text("WAITING", style="yellow")


if __name__ == "__main__":
    app()
