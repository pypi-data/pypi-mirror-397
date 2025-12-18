"""Shared constants for Claude-Linear automation.

This is the single source of truth for all label definitions, colors,
and API endpoints used across the CLI and orchestrator.
"""

# Linear GraphQL API endpoint
LINEAR_GQL = "https://api.linear.app/graphql"

# Issue labels to create (in "Claude" group)
ISSUE_LABELS_CLAUDE_GROUP = [
    "Ready for Claude Code",
    "Claude: queued",
    "Claude: design doc",
    "Claude: design reviewed",
    "Claude: impl plan",
    "Claude: implementing",
    "Claude: dev test",
    "Claude: tests",
    "Claude: cleanup",
    "Claude: pre-commit",
    "Claude: code review",
    "Claude: PR created",
    "Claude: PR review",
    "Claude: PR fixes",
    "Claude: ready for human review",
    "Claude: blocked",
]

# Standalone issue labels (not in a group)
ISSUE_LABELS_STANDALONE = [
    "Ready for human review",
]

# Project labels to create (workspace-wide)
PROJECT_LABELS = [
    "Enhance with Claude",
    "Enhanced with Claude",
    "Create issues with Claude",
    "Issues created with Claude",
    "Claude Project: blocked",
]

# Colors for labels (Linear uses hex without #)
COLORS = {
    "claude_group": "8B5CF6",  # Purple for Claude group
    "claude_project": "6366F1",  # Indigo for Claude Project group
    "ready_trigger": "22C55E",  # Green for trigger labels
    "in_progress": "F59E0B",  # Amber for in-progress
    "blocked": "EF4444",  # Red for blocked
    "review": "3B82F6",  # Blue for review
    "done": "10B981",  # Emerald for done states
}


def get_label_color(name: str) -> str:
    """Get appropriate color for a label based on its name."""
    name_lower = name.lower()
    if "blocked" in name_lower:
        return COLORS["blocked"]
    if "ready for claude" in name_lower or "enhance with claude" in name_lower or "create issues" in name_lower:
        return COLORS["ready_trigger"]
    if "review" in name_lower or "ready for human" in name_lower:
        return COLORS["review"]
    if "enhanced" in name_lower or "created" in name_lower or "pr created" in name_lower:
        return COLORS["done"]
    return COLORS["in_progress"]


# Stage label mapping (Issue flow)
ISSUE_STAGE_TO_LABEL: dict[str, str] = {
    "queued": "Claude: queued",
    "design_doc": "Claude: design doc",
    "design_reviewed": "Claude: design reviewed",
    "impl_plan": "Claude: impl plan",
    "implementing": "Claude: implementing",
    "dev_test": "Claude: dev test",
    "tests": "Claude: tests",
    "cleanup": "Claude: cleanup",
    "precommit": "Claude: pre-commit",
    "code_review": "Claude: code review",
    "pr_created": "Claude: PR created",
    "pr_review": "Claude: PR review",
    "pr_fixes": "Claude: PR fixes",
    "ready": "Claude: ready for human review",
    "blocked": "Claude: blocked",
}

# Stage label mapping (Project flow)
PROJECT_STAGE_TO_LABEL: dict[str, str] = {
    "enhance_queued": "Enhance with Claude",
    "enhanced": "Enhanced with Claude",
    "create_issues": "Create issues with Claude",
    "issues_created": "Issues created with Claude",
    "blocked": "Claude Project: blocked",
}

# Helpful sets for label replacement behavior
ISSUE_ALL_STAGE_LABELS: set[str] = set(ISSUE_STAGE_TO_LABEL.values()) | {"Ready for Claude Code"}
PROJECT_ALL_STAGE_LABELS: set[str] = set(PROJECT_STAGE_TO_LABEL.values())
