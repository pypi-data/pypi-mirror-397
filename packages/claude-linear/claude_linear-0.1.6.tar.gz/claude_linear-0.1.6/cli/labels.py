"""Linear label management.

Functions to create and manage Linear labels for Claude automation.
"""

from typing import Any, cast

import httpx

from shared import (
    COLORS,
    ISSUE_LABELS_CLAUDE_GROUP,
    ISSUE_LABELS_STANDALONE,
    LINEAR_GQL,
    PROJECT_LABELS,
    get_label_color,
)

# Re-export for backwards compatibility
__all__ = [
    "COLORS",
    "ISSUE_LABELS_CLAUDE_GROUP",
    "ISSUE_LABELS_STANDALONE",
    "LINEAR_GQL",
    "PROJECT_LABELS",
    "get_label_color",
    "LinearLabelManager",
]


class LinearLabelManager:
    """Manages Linear labels for Claude automation."""

    def __init__(self, api_key: str):
        """Initialize the label manager.

        Args:
            api_key: Linear API key (starts with lin_api_)
        """
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "LinearLabelManager":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=30)
        return self

    async def __aexit__(self, *args: object) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    async def _gql(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        """Execute a GraphQL query against Linear API."""
        if not self._client:
            raise RuntimeError("Client not initialized. Use async context manager.")

        headers = {
            "Authorization": self.api_key,
            "Content-Type": "application/json",
        }
        r = await self._client.post(
            LINEAR_GQL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"Linear API error ({r.status_code}): {r.text}")
        payload = r.json()
        if payload.get("errors"):
            raise RuntimeError(f"Linear GraphQL error: {payload['errors']}")
        return cast(dict[str, Any], payload["data"])

    async def get_teams(self) -> list[dict[str, Any]]:
        """Get all teams in the workspace.

        Returns:
            List of dicts with 'id', 'key', and 'name' for each team
        """
        q = """
        query {
          teams {
            nodes {
              id
              key
              name
            }
          }
        }
        """
        data = await self._gql(q)
        return cast(list[dict[str, Any]], data["teams"]["nodes"])

    async def get_existing_issue_labels(self, team_id: str) -> dict[str, dict[str, Any]]:
        """Get existing issue labels for a team.

        Args:
            team_id: Linear team ID

        Returns:
            Dict mapping label name to {id, isGroup}
        """
        q = """
        query($teamId: ID) {
          issueLabels(filter: { team: { id: { eq: $teamId } } }, first: 250) {
            nodes {
              id
              name
              isGroup
              parent { id name }
            }
          }
        }
        """
        data = await self._gql(q, {"teamId": team_id})
        return {
            label["name"]: {"id": label["id"], "isGroup": label.get("isGroup", False)}
            for label in data["issueLabels"]["nodes"]
        }

    async def get_existing_project_labels(self) -> dict[str, str]:
        """Get existing project labels.

        Returns:
            Dict mapping label name to label ID
        """
        q = """
        query {
          projectLabels(first: 250) {
            nodes {
              id
              name
            }
          }
        }
        """
        data = await self._gql(q)
        return {label["name"]: label["id"] for label in data["projectLabels"]["nodes"]}

    async def create_issue_label(
        self,
        team_id: str,
        name: str,
        color: str,
        parent_id: str | None = None,
        is_group: bool = False,
    ) -> dict[str, Any]:
        """Create an issue label.

        Args:
            team_id: Linear team ID
            name: Label name
            color: Hex color (without #)
            parent_id: Optional parent label ID for grouping
            is_group: Whether this label is a group

        Returns:
            Created label dict with 'id' and 'name'
        """
        m = """
        mutation($input: IssueLabelCreateInput!) {
          issueLabelCreate(input: $input) {
            success
            issueLabel {
              id
              name
            }
          }
        }
        """
        input_obj: dict[str, Any] = {
            "teamId": team_id,
            "name": name,
            "color": color,
        }
        if parent_id:
            input_obj["parentId"] = parent_id
        if is_group:
            input_obj["isGroup"] = True

        data = await self._gql(m, {"input": input_obj})
        return cast(dict[str, Any], data["issueLabelCreate"]["issueLabel"])

    async def update_issue_label_to_group(self, label_id: str) -> None:
        """Update an existing label to be a group.

        Args:
            label_id: Label ID to update
        """
        m = """
        mutation($id: String!, $input: IssueLabelUpdateInput!) {
          issueLabelUpdate(id: $id, input: $input) {
            success
          }
        }
        """
        await self._gql(m, {"id": label_id, "input": {"isGroup": True}})

    async def create_project_label(self, name: str, color: str) -> dict[str, Any]:
        """Create a project label.

        Args:
            name: Label name
            color: Hex color (without #)

        Returns:
            Created label dict with 'id' and 'name'
        """
        m = """
        mutation($input: ProjectLabelCreateInput!) {
          projectLabelCreate(input: $input) {
            success
            projectLabel {
              id
              name
            }
          }
        }
        """
        data = await self._gql(m, {"input": {"name": name, "color": color}})
        return cast(dict[str, Any], data["projectLabelCreate"]["projectLabel"])

    async def _get_workspace_issue_labels(self) -> dict[str, dict[str, Any]]:
        """Get all issue labels in the workspace (regardless of team).

        Returns:
            Dict mapping label name to {id, isGroup, teamId}
        """
        q = """
        query {
          issueLabels(first: 250) {
            nodes {
              id
              name
              isGroup
              parent { id name }
              team { id }
            }
          }
        }
        """
        data = await self._gql(q)
        return {
            label["name"]: {
                "id": label["id"],
                "isGroup": label.get("isGroup", False),
                "teamId": label.get("team", {}).get("id") if label.get("team") else None,
            }
            for label in data["issueLabels"]["nodes"]
        }

    async def _try_create_issue_label(
        self,
        team_id: str,
        name: str,
        color: str,
        parent_id: str | None = None,
        is_group: bool = False,
    ) -> tuple[dict[str, Any] | None, bool]:
        """Try to create an issue label, handling duplicates gracefully.

        Args:
            team_id: Linear team ID
            name: Label name
            color: Hex color (without #)
            parent_id: Optional parent label ID for grouping
            is_group: Whether this label is a group

        Returns:
            Tuple of (label_dict or None, was_created)
            If duplicate, returns (None, False)
        """
        try:
            label = await self.create_issue_label(team_id, name, color, parent_id, is_group)
            return label, True
        except RuntimeError as e:
            error_str = str(e).lower()
            # Handle duplicate labels and team mismatch (label exists for different team)
            if "duplicate label name" in error_str or "team mismatch" in error_str:
                return None, False
            raise

    async def setup_issue_labels(self, team_id: str) -> tuple[int, int]:
        """Create all issue labels for a team.

        Args:
            team_id: Linear team ID

        Returns:
            Tuple of (created_count, existing_count)
        """
        from .utils import print_info, print_success

        existing = await self.get_existing_issue_labels(team_id)
        created = 0
        skipped = 0

        # First, create the "Claude" parent label (group)
        # Check team-specific labels first
        claude_info = existing.get("Claude")
        claude_group_id: str | None = None

        if claude_info:
            # Found in team-specific labels - use it
            claude_group_id = claude_info["id"]
            if not claude_info["isGroup"]:
                await self.update_issue_label_to_group(claude_group_id)
                print_info("Converted 'Claude' to group")
            else:
                print_info("'Claude' group already exists")
            skipped += 1
        else:
            # Check workspace labels to see if one exists
            workspace_labels = await self._get_workspace_issue_labels()
            workspace_claude = workspace_labels.get("Claude")

            # Only use workspace label if it's workspace-level (no team) or belongs to this team
            if workspace_claude:
                label_team_id = workspace_claude.get("teamId")
                if label_team_id is None or label_team_id == team_id:
                    # Workspace-level or same team - safe to use
                    claude_group_id = workspace_claude["id"]
                    if not workspace_claude["isGroup"]:
                        await self.update_issue_label_to_group(claude_group_id)
                        print_info("Converted 'Claude' to group")
                    else:
                        print_info("'Claude' group already exists in workspace")
                    skipped += 1
                # else: belongs to different team, need to create team-specific one

            if not claude_group_id:
                # Create new team-specific Claude group
                label, was_created = await self._try_create_issue_label(
                    team_id, "Claude", COLORS["claude_group"], is_group=True
                )
                if was_created and label:
                    claude_group_id = label["id"]
                    print_success("Created 'Claude' label group")
                    created += 1
                else:
                    # Race condition: label was created between our check and create attempt
                    # Re-fetch team-specific labels
                    existing = await self.get_existing_issue_labels(team_id)
                    claude_info = existing.get("Claude")
                    if claude_info:
                        claude_group_id = claude_info["id"]
                        print_info("'Claude' group already exists")
                        skipped += 1
                    else:
                        raise RuntimeError("Failed to create or find 'Claude' label for team")

        # Create labels in the Claude group
        for label_name in ISSUE_LABELS_CLAUDE_GROUP:
            if label_name in existing:
                print_info(f"'{label_name}' already exists")
                skipped += 1
                continue
            color = get_label_color(label_name)
            _, was_created = await self._try_create_issue_label(team_id, label_name, color, claude_group_id)
            if was_created:
                print_success(f"Created '{label_name}'")
                created += 1
            else:
                print_info(f"'{label_name}' already exists in workspace")
                skipped += 1

        # Create standalone labels
        for label_name in ISSUE_LABELS_STANDALONE:
            if label_name in existing:
                print_info(f"'{label_name}' already exists")
                skipped += 1
                continue
            color = get_label_color(label_name)
            _, was_created = await self._try_create_issue_label(team_id, label_name, color)
            if was_created:
                print_success(f"Created '{label_name}'")
                created += 1
            else:
                print_info(f"'{label_name}' already exists in workspace")
                skipped += 1

        return created, skipped

    async def _try_create_project_label(self, name: str, color: str) -> tuple[dict[str, Any] | None, bool]:
        """Try to create a project label, handling duplicates gracefully.

        Args:
            name: Label name
            color: Hex color (without #)

        Returns:
            Tuple of (label_dict or None, was_created)
            If duplicate, returns (None, False)
        """
        try:
            label = await self.create_project_label(name, color)
            return label, True
        except RuntimeError as e:
            if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                return None, False
            raise

    async def setup_project_labels(self) -> tuple[int, int]:
        """Create all project labels.

        Returns:
            Tuple of (created_count, existing_count)
        """
        from .utils import print_info, print_success

        existing = await self.get_existing_project_labels()
        created = 0
        skipped = 0

        for label_name in PROJECT_LABELS:
            if label_name in existing:
                print_info(f"'{label_name}' already exists")
                skipped += 1
                continue
            color = get_label_color(label_name)
            _, was_created = await self._try_create_project_label(label_name, color)
            if was_created:
                print_success(f"Created '{label_name}'")
                created += 1
            else:
                print_info(f"'{label_name}' already exists")
                skipped += 1

        return created, skipped

    async def count_labels(self, team_id: str) -> tuple[int, int]:
        """Count existing Claude labels.

        Args:
            team_id: Linear team ID

        Returns:
            Tuple of (issue_labels_count, project_labels_count)
        """
        issue_labels = await self.get_existing_issue_labels(team_id)
        project_labels = await self.get_existing_project_labels()

        # Count issue labels we care about
        expected_issue = set(ISSUE_LABELS_CLAUDE_GROUP + ISSUE_LABELS_STANDALONE + ["Claude"])
        issue_count = len(expected_issue & set(issue_labels.keys()))

        # Count project labels we care about
        expected_project = set(PROJECT_LABELS)
        project_count = len(expected_project & set(project_labels.keys()))

        return issue_count, project_count
