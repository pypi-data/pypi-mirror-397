"""Interactive setup wizard for Claude-Linear automation."""

import asyncio
from typing import Any

from .labels import LinearLabelManager
from .utils import (
    check_linear_connection,
    fatal_error,
    generate_secret,
    mask_secret,
    print_box,
    print_error,
    print_header,
    print_info,
    print_success,
)


def prompt_input(message: str, default: str | None = None, secret: bool = False) -> str:
    """Prompt user for input with optional default.

    Args:
        message: Prompt message to display
        default: Default value if user presses Enter
        secret: Whether to mask input (for passwords/keys)

    Returns:
        User input or default value
    """
    prompt = f"{message} [{mask_secret(default) if secret else default}]: " if default else f"{message}: "

    try:
        value = input(prompt).strip()
        return value if value else (default or "")
    except (KeyboardInterrupt, EOFError):
        print("\n")
        fatal_error("Setup cancelled")


def prompt_choice(message: str, options: list[tuple[str, str]]) -> str:
    """Prompt user to choose from options.

    Args:
        message: Prompt message to display
        options: List of (value, display_text) tuples

    Returns:
        Selected option value
    """
    print(f"\n{message}")
    for i, (_, display) in enumerate(options, 1):
        print(f"  {i}. {display}")

    while True:
        try:
            choice = input(f"\nSelect (1-{len(options)}): ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx][0]
            print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a number")
        except (KeyboardInterrupt, EOFError):
            print("\n")
            fatal_error("Setup cancelled")


async def select_team(manager: LinearLabelManager) -> list[dict[str, Any]]:
    """Prompt user to select a Linear team or all teams.

    Args:
        manager: Initialized LinearLabelManager

    Returns:
        List of selected team dicts, each with 'id', 'key', 'name'
    """
    teams = await manager.get_teams()

    if not teams:
        fatal_error("No teams found in your Linear workspace")

    if len(teams) == 1:
        print_info(f"Using team: {teams[0]['name']} ({teams[0]['key']})")
        return [teams[0]]

    # Add "All teams" option at the beginning
    options: list[tuple[str, str]] = [("__all__", "All teams")]
    options.extend([(t["id"], f"{t['key']}: {t['name']}") for t in teams])
    selection = prompt_choice("Select Linear team for labels:", options)

    if selection == "__all__":
        print_info(f"Selected all {len(teams)} teams")
        return teams

    selected_team = next(t for t in teams if t["id"] == selection)
    return [selected_team]


async def run_setup(
    linear_api_key: str | None = None,
    skip_labels: bool = False,
) -> dict[str, str]:
    """Run the interactive setup wizard.

    Args:
        linear_api_key: Optional pre-provided Linear API key
        skip_labels: Whether to skip label creation

    Returns:
        Dict of generated/collected configuration values
    """
    print("\n" + "=" * 60)
    print("     Claude-Linear Automation Setup")
    print("=" * 60)

    config: dict[str, str] = {}

    # Step 1: Linear API Key
    print_header("Step 1/5: Linear API Key")
    print("  Get your API key from: Linear Settings > API > Personal API Keys")

    api_key = linear_api_key if linear_api_key else prompt_input("  Enter your Linear API key")

    if not api_key.startswith("lin_api_"):
        print_error("API key should start with 'lin_api_'")
        fatal_error("Invalid Linear API key format")

    # Verify connection
    try:
        org_info = await check_linear_connection(api_key)
        print_success(f"Connected to workspace: {org_info['name']}")
        config["LINEAR_API_KEY"] = api_key
    except RuntimeError as e:
        fatal_error(str(e))

    # Step 2: Select Team and Create Labels
    print_header("Step 2/5: Linear Labels")

    async with LinearLabelManager(api_key) as manager:
        teams = await select_team(manager)
        # Use the first team as the default
        config["DEFAULT_LINEAR_TEAM_ID"] = teams[0]["id"]

        if not skip_labels:
            total_created = 0
            total_existing = 0

            for team in teams:
                print_info(f"Creating issue labels for {team['key']}...")
                created_issue, existing_issue = await manager.setup_issue_labels(team["id"])
                total_created += created_issue
                total_existing += existing_issue

            print_info("Creating project labels...")
            created_project, existing_project = await manager.setup_project_labels()
            total_created += created_project
            total_existing += existing_project

            print_success(f"Labels ready: {total_created} created, {total_existing} already existed")
        else:
            print_info("Skipping label creation")

        # Store the first team for display purposes
        team = teams[0]

    # Step 3: Generate Secrets
    print_header("Step 3/5: Generate Secrets")

    agent_secret = generate_secret(32)
    print_success(f"Generated AGENT_SHARED_SECRET: {mask_secret(agent_secret, 8)}")
    config["AGENT_SHARED_SECRET"] = agent_secret

    # Step 4: Display Vercel Environment Variables
    print_header("Step 4/5: Vercel Environment Variables")
    print_box(
        "Copy to Vercel > Settings > Environment Variables:",
        [
            f"LINEAR_API_KEY={mask_secret(api_key)}",
            "LINEAR_WEBHOOK_SECRET=<from Linear webhook settings>",
            "GITHUB_DISPATCH_TOKEN=<your GitHub PAT with repo scope>",
            f"AGENT_SHARED_SECRET={agent_secret}",
            f"DEFAULT_LINEAR_TEAM_ID={team['id']}",
        ],
    )
    print("\n  Note: Get LINEAR_WEBHOOK_SECRET after creating the webhook in Linear")
    print("  Note: Create GITHUB_DISPATCH_TOKEN at GitHub Settings > Developer > PAT")

    # Step 5: Display GitHub Repository Secrets
    print_header("Step 5/5: GitHub Repository Secrets")
    print_box(
        "Add to each repo > Settings > Secrets > Actions:",
        [
            "ANTHROPIC_API_KEY=<your Anthropic API key>",
            "CLAUDE_AGENT_API_BASE=<your Vercel deployment URL>",
            f"CLAUDE_AGENT_TOKEN={agent_secret}",
        ],
    )

    # Next Steps
    print("\n" + "=" * 60)
    print_success("Setup complete!")
    print("=" * 60)
    print("""
Next steps:
  1. Deploy orchestrator to Vercel:
     cd orchestrator && vercel deploy

  2. Create webhook in Linear:
     Linear Settings > API > Webhooks
     URL: https://your-app.vercel.app/webhooks/linear
     Enable: Issues, Projects

  3. Copy LINEAR_WEBHOOK_SECRET to Vercel env vars

  4. Install templates in your repos:
     claude-linear init /path/to/repo

  5. Add a 'Ready for Claude Code' label to any issue to start!
""")

    return config


def setup_command(
    linear_api_key: str | None = None,
    skip_labels: bool = False,
) -> None:
    """Entry point for the setup command.

    Args:
        linear_api_key: Optional pre-provided Linear API key
        skip_labels: Whether to skip label creation
    """
    asyncio.run(run_setup(linear_api_key, skip_labels))
