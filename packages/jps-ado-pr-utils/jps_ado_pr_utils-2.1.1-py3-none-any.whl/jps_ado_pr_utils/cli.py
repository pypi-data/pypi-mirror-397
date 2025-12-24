#!/usr/bin/env python3
"""
Main CLI entry point for jps-ado-pr-utils.

Provides commands for:
- list: List pull requests
- create: Create pull requests
"""

import typer

from jps_ado_pr_utils.create_pr import create
from jps_ado_pr_utils.list_open_prs import list_prs

app = typer.Typer(
    name="jps-ado-pr-utils",
    help="Azure DevOps Pull Request Utilities",
    no_args_is_help=True,
)

# Add subcommands
app.command(name="list", help="List pull requests")(list_prs)
app.command(name="create", help="Create a pull request")(create)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
