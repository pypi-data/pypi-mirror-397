"""Claude-Linear CLI - Main entry point.

Usage:
    claude-linear setup      # Interactive setup wizard
    claude-linear validate   # Validate configuration
    claude-linear init       # Install templates to a repo
    claude-linear labels     # Manage Linear labels
    claude-linear version    # Show version info
"""

import sys

import click

from . import __version__


@click.group()
@click.version_option(version=__version__, prog_name="claude-linear")
def cli() -> None:
    """Claude-Linear Automation CLI.

    Automate software development with Claude Code, Linear, and GitHub Actions.

    Run 'claude-linear setup' to get started.
    """
    pass


@cli.command()
@click.option(
    "--linear-api-key",
    envvar="LINEAR_API_KEY",
    help="Linear API key (or set LINEAR_API_KEY env var)",
)
@click.option(
    "--skip-labels",
    is_flag=True,
    help="Skip creating Linear labels",
)
def setup(linear_api_key: str | None, skip_labels: bool) -> None:
    """Interactive setup wizard.

    Guides you through:
    - Connecting to Linear
    - Creating required labels
    - Generating secrets
    - Configuring Vercel and GitHub
    """
    from .setup import setup_command

    setup_command(linear_api_key, skip_labels)


@cli.command()
@click.option(
    "--api-base",
    envvar="CLAUDE_AGENT_API_BASE",
    help="Orchestrator base URL",
)
@click.option(
    "--linear-api-key",
    envvar="LINEAR_API_KEY",
    help="Linear API key",
)
@click.option(
    "--github-token",
    envvar="GITHUB_DISPATCH_TOKEN",
    help="GitHub personal access token",
)
@click.option(
    "--agent-token",
    envvar="CLAUDE_AGENT_TOKEN",
    help="Agent shared secret",
)
@click.option(
    "--team-id",
    envvar="DEFAULT_LINEAR_TEAM_ID",
    help="Linear team ID",
)
def validate(
    api_base: str | None,
    linear_api_key: str | None,
    github_token: str | None,
    agent_token: str | None,
    team_id: str | None,
) -> None:
    """Validate configuration.

    Checks:
    - Orchestrator health and authentication
    - Linear API connectivity and labels
    - GitHub token permissions
    """
    from .validate import validate_command

    failures = validate_command(api_base, linear_api_key, github_token, agent_token, team_id)
    sys.exit(failures)


@cli.command()
@click.argument("target_dir", default=".", type=click.Path(exists=True))
@click.option(
    "--force",
    is_flag=True,
    help="Overwrite existing files",
)
@click.option(
    "--skip-workflow",
    is_flag=True,
    help="Don't install GitHub Actions workflow",
)
@click.option(
    "--skip-runner",
    is_flag=True,
    help="Don't install runner script",
)
@click.option(
    "--skip-config",
    is_flag=True,
    help="Don't install example automation.yml",
)
def init(
    target_dir: str,
    force: bool,
    skip_workflow: bool,
    skip_runner: bool,
    skip_config: bool,
) -> None:
    """Install templates to a repository.

    Installs:
    - .github/workflows/claude-linear.yml (GitHub Actions workflow)
    - scripts/claude_linear_runner.py (Runner script)
    - .claude/automation.yml (Example configuration)

    TARGET_DIR defaults to current directory.
    """
    from .init import init_command

    init_command(target_dir, force, skip_workflow, skip_runner, skip_config)


@cli.command()
@click.option(
    "--linear-api-key",
    envvar="LINEAR_API_KEY",
    help="Linear API key",
)
@click.option(
    "--team",
    "-t",
    help="Team key (e.g., 'ENG')",
)
@click.option(
    "--all-teams",
    "-a",
    is_flag=True,
    help="Create labels for all teams",
)
@click.option(
    "--skip-issue-labels",
    is_flag=True,
    help="Skip creating issue labels",
)
@click.option(
    "--skip-project-labels",
    is_flag=True,
    help="Skip creating project labels",
)
def labels(
    linear_api_key: str | None,
    team: str | None,
    all_teams: bool,
    skip_issue_labels: bool,
    skip_project_labels: bool,
) -> None:
    """Manage Linear labels.

    Creates all required labels for Claude automation:
    - Issue labels in the "Claude" group
    - Project labels for project flows
    """
    import asyncio

    from .labels import LinearLabelManager
    from .utils import fatal_error, print_header, print_success

    if not linear_api_key:
        fatal_error("LINEAR_API_KEY is required. Set via --linear-api-key or environment variable.")

    async def run() -> None:
        async with LinearLabelManager(linear_api_key) as manager:
            teams = await manager.get_teams()

            if not teams:
                fatal_error("No teams found in workspace")

            teams_to_process = []

            if all_teams:
                teams_to_process = teams
                print(f"Creating labels for all {len(teams)} teams...")
            elif team:
                t = next((t for t in teams if t["key"].lower() == team.lower()), None)
                if not t:
                    fatal_error(f"Team '{team}' not found. Available: {', '.join(t['key'] for t in teams)}")
                teams_to_process = [t]
            else:
                # Interactive selection if only one command
                if len(teams) == 1:
                    teams_to_process = [teams[0]]
                else:
                    print("Available teams:")
                    for i, t in enumerate(teams, 1):
                        print(f"  {i}. {t['key']}: {t['name']}")
                    while True:
                        try:
                            choice = input(f"\nSelect team (1-{len(teams)}): ").strip()
                            idx = int(choice) - 1
                            if 0 <= idx < len(teams):
                                teams_to_process = [teams[idx]]
                                break
                        except (ValueError, KeyboardInterrupt):
                            fatal_error("Invalid selection or cancelled")

            project_labels_done = False
            for t in teams_to_process:
                print_header(f"Team: {t['name']} ({t['key']})")

                if not skip_issue_labels:
                    created, existing = await manager.setup_issue_labels(t["id"])
                    print_success(f"Issue labels: {created} created, {existing} existing")

                if not skip_project_labels and not project_labels_done:
                    created, existing = await manager.setup_project_labels()
                    print_success(f"Project labels: {created} created, {existing} existing")
                    project_labels_done = True

            print_success("Label setup complete!")

    asyncio.run(run())


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
