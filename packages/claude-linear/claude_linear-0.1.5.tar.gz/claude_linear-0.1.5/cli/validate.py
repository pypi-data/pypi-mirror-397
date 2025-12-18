"""Configuration validation for Claude-Linear automation."""

import asyncio
import os
import re

import httpx

from .labels import ISSUE_LABELS_CLAUDE_GROUP, ISSUE_LABELS_STANDALONE, PROJECT_LABELS, LinearLabelManager
from .utils import (
    check_linear_connection,
    check_orchestrator_health,
    print_error,
    print_header,
    print_info,
    print_success,
)


async def validate_linear_api_key(api_key: str) -> tuple[bool, str]:
    """Validate Linear API key.

    Args:
        api_key: Linear API key to validate

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_key:
        return False, "LINEAR_API_KEY not set"

    if not api_key.startswith("lin_api_"):
        return False, f"Invalid format: should start with 'lin_api_', got '{api_key[:10]}...'"

    try:
        org_info = await check_linear_connection(api_key)
        return True, f"Connected to '{org_info['name']}'"
    except RuntimeError as e:
        return False, str(e)


async def validate_linear_labels(api_key: str, team_id: str | None = None) -> tuple[bool, str]:
    """Validate that required Linear labels exist.

    Args:
        api_key: Linear API key
        team_id: Optional team ID (will use first team if not provided)

    Returns:
        Tuple of (is_valid, message)
    """
    async with LinearLabelManager(api_key) as manager:
        teams = await manager.get_teams()
        if not teams:
            return False, "No teams found"

        if team_id:
            team = next((t for t in teams if t["id"] == team_id), None)
            if not team:
                return False, f"Team ID '{team_id}' not found"
        else:
            team = teams[0]

        issue_count, project_count = await manager.count_labels(team["id"])

        expected_issue = len(ISSUE_LABELS_CLAUDE_GROUP) + len(ISSUE_LABELS_STANDALONE) + 1  # +1 for Claude group
        expected_project = len(PROJECT_LABELS)

        if issue_count >= expected_issue and project_count >= expected_project:
            return (
                True,
                f"All labels present ({issue_count}/{expected_issue} issue, {project_count}/{expected_project} project)",
            )

        missing = []
        if issue_count < expected_issue:
            missing.append(f"issue labels: {issue_count}/{expected_issue}")
        if project_count < expected_project:
            missing.append(f"project labels: {project_count}/{expected_project}")

        return False, f"Missing {', '.join(missing)}. Run 'claude-linear setup' to create."


async def validate_github_token(token: str) -> tuple[bool, str]:
    """Validate GitHub token has required scopes.

    Args:
        token: GitHub personal access token

    Returns:
        Tuple of (is_valid, message)
    """
    if not token:
        return False, "GITHUB_DISPATCH_TOKEN not set"

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )

            if r.status_code == 401:
                return False, "Invalid token - authentication failed"

            if r.status_code != 200:
                return False, f"GitHub API error: {r.status_code}"

            # Check X-OAuth-Scopes header for required scopes
            scopes = r.headers.get("X-OAuth-Scopes", "")
            scope_list = [s.strip() for s in scopes.split(",")]

            if "repo" not in scope_list:
                return False, f"Missing 'repo' scope. Current scopes: {scopes}"

            user = r.json()
            return True, f"Authenticated as '{user.get('login')}' with repo scope"

        except httpx.TimeoutException:
            return False, "Timeout connecting to GitHub"
        except Exception as e:
            return False, f"Error: {e}"


async def validate_orchestrator(api_base: str, agent_token: str | None = None) -> tuple[bool, str]:
    """Validate orchestrator deployment.

    Args:
        api_base: Base URL of the orchestrator
        agent_token: Optional agent token to test authentication

    Returns:
        Tuple of (is_valid, message)
    """
    if not api_base:
        return False, "CLAUDE_AGENT_API_BASE not set"

    # Normalize URL
    api_base = api_base.rstrip("/")
    if not re.match(r"^https?://", api_base):
        api_base = f"https://{api_base}"

    # Check health endpoint
    if not await check_orchestrator_health(api_base):
        return False, f"Health check failed at {api_base}/health"

    # If agent token provided, test authenticated endpoint
    if agent_token:
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                # Try to call an agent endpoint - should return 404 for invalid ID, not 401
                r = await client.get(
                    f"{api_base}/agent/context/issue/test-id",
                    headers={"X-Agent-Token": agent_token},
                )
                if r.status_code == 401:
                    return False, "Agent token authentication failed"
                # 404 is expected for invalid ID - auth succeeded
            except Exception as e:
                return False, f"Error testing agent auth: {e}"

        return True, f"Orchestrator healthy at {api_base} (agent auth OK)"

    return True, f"Orchestrator healthy at {api_base}"


async def run_validation(
    api_base: str | None = None,
    linear_api_key: str | None = None,
    github_token: str | None = None,
    agent_token: str | None = None,
    team_id: str | None = None,
) -> int:
    """Run all configuration validations.

    Args:
        api_base: Orchestrator base URL
        linear_api_key: Linear API key
        github_token: GitHub PAT
        agent_token: Agent shared secret
        team_id: Linear team ID

    Returns:
        Number of failed validations
    """
    # Load from environment if not provided
    api_base = api_base or os.environ.get("CLAUDE_AGENT_API_BASE")
    linear_api_key = linear_api_key or os.environ.get("LINEAR_API_KEY")
    github_token = github_token or os.environ.get("GITHUB_DISPATCH_TOKEN")
    agent_token = agent_token or os.environ.get("AGENT_SHARED_SECRET") or os.environ.get("CLAUDE_AGENT_TOKEN")
    team_id = team_id or os.environ.get("DEFAULT_LINEAR_TEAM_ID")

    print("\n" + "=" * 60)
    print("     Claude-Linear Configuration Validator")
    print("=" * 60)
    print("\nValidating configuration...")

    failures = 0

    # Validate orchestrator
    print_header("Orchestrator")
    if api_base:
        valid, msg = await validate_orchestrator(api_base, agent_token)
        if valid:
            print_success(msg)
        else:
            print_error(msg)
            failures += 1
    else:
        print_error("CLAUDE_AGENT_API_BASE not configured")
        failures += 1

    # Validate Linear API key
    print_header("Linear API")
    if linear_api_key:
        valid, msg = await validate_linear_api_key(linear_api_key)
        if valid:
            print_success(msg)

            # Check labels
            valid, msg = await validate_linear_labels(linear_api_key, team_id)
            if valid:
                print_success(msg)
            else:
                print_error(msg)
                failures += 1
        else:
            print_error(msg)
            failures += 1
    else:
        print_error("LINEAR_API_KEY not configured")
        failures += 1

    # Validate GitHub token
    print_header("GitHub Token")
    if github_token:
        valid, msg = await validate_github_token(github_token)
        if valid:
            print_success(msg)
        else:
            print_error(msg)
            failures += 1
    else:
        print_info("GITHUB_DISPATCH_TOKEN not configured (optional for validation)")

    # Summary
    print("\n" + "=" * 60)
    if failures == 0:
        print_success("All validations passed!")
    else:
        print_error(f"{failures} validation(s) failed")
        print_info("See docs/TROUBLESHOOTING.md for help")
    print("=" * 60 + "\n")

    return failures


def validate_command(
    api_base: str | None = None,
    linear_api_key: str | None = None,
    github_token: str | None = None,
    agent_token: str | None = None,
    team_id: str | None = None,
) -> int:
    """Entry point for the validate command.

    Args:
        api_base: Orchestrator base URL
        linear_api_key: Linear API key
        github_token: GitHub PAT
        agent_token: Agent shared secret
        team_id: Linear team ID

    Returns:
        Exit code (0 = success, >0 = number of failures)
    """
    return asyncio.run(run_validation(api_base, linear_api_key, github_token, agent_token, team_id))
