"""Tests for CLI utilities and commands."""

import re

from cli.utils import generate_secret, mask_secret


class TestGenerateSecret:
    """Test suite for secret generation."""

    def test_generates_hex_string(self) -> None:
        """Generated secret should be valid hex."""
        secret = generate_secret()

        # Should be valid hex (no error when parsing)
        int(secret, 16)

    def test_correct_length(self) -> None:
        """Generated secret should have correct length."""
        # Default 32 bytes = 64 hex chars
        secret = generate_secret()
        assert len(secret) == 64

        # Custom length
        secret = generate_secret(16)
        assert len(secret) == 32

    def test_uniqueness(self) -> None:
        """Each generated secret should be unique."""
        secrets = {generate_secret() for _ in range(100)}

        # All should be unique
        assert len(secrets) == 100

    def test_cryptographically_random(self) -> None:
        """Secret should be cryptographically random (basic entropy check)."""
        secret = generate_secret()

        # Check it's not all zeros or repeated pattern
        assert secret != "0" * 64
        assert len(set(secret)) > 4  # At least 5 different characters


class TestMaskSecret:
    """Test suite for secret masking."""

    def test_masks_most_of_secret(self) -> None:
        """Should mask most of the secret, showing only first few chars."""
        masked = mask_secret("lin_api_abcdef12345")

        assert masked.startswith("lin_")
        assert "abcdef12345" not in masked
        assert "*" in masked

    def test_custom_visible_chars(self) -> None:
        """Should allow customizing visible characters."""
        masked = mask_secret("secretvalue", visible_chars=6)

        assert masked.startswith("secret")
        assert "value" not in masked

    def test_short_secrets(self) -> None:
        """Should handle secrets shorter than visible_chars."""
        masked = mask_secret("abc", visible_chars=10)

        # Should just mask entirely
        assert "abc" not in masked
        assert "*" in masked

    def test_empty_string(self) -> None:
        """Should handle empty string."""
        masked = mask_secret("")
        assert masked == ""


class TestCLIStructure:
    """Test that CLI commands are properly structured."""

    def test_cli_imports(self) -> None:
        """CLI modules should import without error."""

    def test_cli_has_version(self) -> None:
        """CLI should have version defined."""
        from cli import __version__

        assert __version__
        assert re.match(r"\d+\.\d+\.\d+", __version__)

    def test_main_cli_group_exists(self) -> None:
        """Main CLI group should exist."""
        from cli.main import cli

        # Should be a click group
        assert hasattr(cli, "commands")

    def test_all_commands_registered(self) -> None:
        """All expected commands should be registered."""
        from cli.main import cli

        expected_commands = {"setup", "validate", "init", "labels"}
        actual_commands = set(cli.commands.keys())

        assert expected_commands.issubset(actual_commands)
