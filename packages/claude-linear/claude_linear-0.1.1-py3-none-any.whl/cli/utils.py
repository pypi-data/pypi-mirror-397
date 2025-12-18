"""Shared utilities for the CLI."""

import secrets
import sys
from typing import NoReturn

import httpx


def generate_secret(length: int = 32) -> str:
    """Generate a cryptographically secure random secret.

    Args:
        length: Number of random bytes (will be hex-encoded to 2x length)

    Returns:
        Hex-encoded random string
    """
    return secrets.token_hex(length)


def print_message(message: str, msg_type: str = "info") -> None:
    """Print a formatted message.

    Args:
        message: The message to print
        msg_type: One of "success", "error", or "info"
    """
    prefixes = {
        "success": "\033[32m✓\033[0m",
        "error": "\033[31m✗\033[0m",
        "info": "→",
    }
    print(f"  {prefixes.get(msg_type, '→')} {message}")


def print_success(message: str) -> None:
    """Print a success message with green checkmark."""
    print_message(message, "success")


def print_error(message: str) -> None:
    """Print an error message with red X."""
    print_message(message, "error")


def print_info(message: str) -> None:
    """Print an info message with arrow."""
    print_message(message, "info")


def print_header(message: str) -> None:
    """Print a header message."""
    print(f"\n\033[1m{message}\033[0m")


def print_box(title: str, lines: list[str]) -> None:
    """Print content in a box."""
    max_len = max(len(title), max(len(line) for line in lines)) + 2
    border = "─" * max_len

    print(f"  ┌{border}┐")
    print(f"  │ {title.ljust(max_len - 2)} │")
    print(f"  ├{border}┤")
    for line in lines:
        print(f"  │ {line.ljust(max_len - 2)} │")
    print(f"  └{border}┘")


def fatal_error(message: str) -> NoReturn:
    """Print an error message and exit."""
    print(f"\n\033[31m❌ Error: {message}\033[0m", file=sys.stderr)
    sys.exit(1)


async def check_linear_connection(api_key: str) -> dict[str, str]:
    """Verify Linear API key and return workspace info.

    Args:
        api_key: Linear API key

    Returns:
        Dict with 'id' and 'name' of the organization

    Raises:
        RuntimeError: If connection fails
    """
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(
            "https://api.linear.app/graphql",
            json={"query": "{ viewer { id name } organization { id name } }"},
            headers={"Authorization": api_key, "Content-Type": "application/json"},
        )

        if r.status_code == 401:
            raise RuntimeError("Invalid API key - authentication failed")

        if r.status_code >= 400:
            raise RuntimeError(f"Linear API error: {r.status_code}")

        data = r.json()
        if data.get("errors"):
            raise RuntimeError(f"GraphQL error: {data['errors']}")

        org = data["data"]["organization"]
        return {"id": org["id"], "name": org["name"]}


async def check_orchestrator_health(api_base: str) -> bool:
    """Check if the orchestrator is healthy.

    Args:
        api_base: Base URL of the orchestrator (e.g., https://your-app.vercel.app)

    Returns:
        True if healthy, False otherwise
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            r = await client.get(f"{api_base.rstrip('/')}/health")
            return r.status_code == 200 and r.json().get("status") == "ok"
        except Exception:
            return False


def mask_secret(value: str, visible_chars: int = 4) -> str:
    """Mask a secret value, showing only first few characters.

    Args:
        value: The secret to mask
        visible_chars: Number of characters to show

    Returns:
        Masked string like "lin_api_****..."
    """
    if len(value) <= visible_chars:
        return "*" * len(value)
    return value[:visible_chars] + "*" * (len(value) - visible_chars - 3) + "..."
