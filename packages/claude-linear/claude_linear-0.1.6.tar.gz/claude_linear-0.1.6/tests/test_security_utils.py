"""Tests for security utilities (error sanitization)."""

from src.security_utils import (
    create_safe_error_comment,
    sanitize_error_message,
)


class TestSanitizeErrorMessage:
    """Test suite for error message sanitization."""

    def test_none_error_returns_generic_message(self) -> None:
        """None errors should return a generic message."""
        assert sanitize_error_message(None) == "An unexpected error occurred"

    def test_simple_safe_error_preserved(self) -> None:
        """Simple safe error messages should be preserved."""
        assert sanitize_error_message("Missing required field") == "Missing required field"
        assert sanitize_error_message("Invalid input") == "Invalid input"
        assert sanitize_error_message("Not found") == "Not found"

    def test_api_key_redacted(self) -> None:
        """API keys should be redacted."""
        msg = "Error with api_key=sk-ant-abc123def456"
        result = sanitize_error_message(msg)
        assert "sk-ant-" not in result
        assert "[REDACTED]" in result

    def test_linear_api_key_redacted(self) -> None:
        """Linear API keys should be redacted."""
        msg = "Authentication failed with lin_api_abc123xyz789"
        result = sanitize_error_message(msg)
        assert "lin_api_" not in result
        assert "[REDACTED]" in result

    def test_github_token_redacted(self) -> None:
        """GitHub tokens should be redacted."""
        msg = "GitHub error: token ghp_abc123XYZ789 is invalid"
        result = sanitize_error_message(msg)
        assert "ghp_" not in result
        assert "[REDACTED]" in result

    def test_bearer_token_redacted(self) -> None:
        """Bearer tokens should be redacted."""
        msg = "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
        result = sanitize_error_message(msg)
        assert "Bearer" not in result or "eyJ" not in result
        assert "[REDACTED]" in result

    def test_connection_string_redacted(self) -> None:
        """Database connection strings should be redacted."""
        msg = "Failed to connect: postgres://user:pass@localhost:5432/db"
        result = sanitize_error_message(msg)
        assert "postgres://" not in result
        assert "[REDACTED]" in result

    def test_internal_ip_redacted(self) -> None:
        """Internal IP addresses should be redacted."""
        msg = "Cannot reach server at 192.168.1.100:8080"
        result = sanitize_error_message(msg)
        assert "192.168.1.100" not in result
        assert "[REDACTED]" in result

    def test_long_hex_string_redacted(self) -> None:
        """Long hex strings (potential secrets) should be redacted."""
        # 64-char hex string (typical for secrets like AGENT_SHARED_SECRET)
        hex_secret = "a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2"
        msg = f"Invalid token: {hex_secret} was rejected"
        result = sanitize_error_message(msg)
        assert hex_secret not in result
        assert "[REDACTED]" in result

    def test_jwt_redacted(self) -> None:
        """JWT tokens should be redacted."""
        msg = "Token expired: eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0"
        result = sanitize_error_message(msg)
        assert "eyJ" not in result
        assert "[REDACTED]" in result

    def test_message_truncated(self) -> None:
        """Long messages should be truncated."""
        long_msg = "Error: " + "x" * 500
        result = sanitize_error_message(long_msg, max_length=100)
        assert len(result) <= 100
        assert result.endswith("...")

    def test_exception_object_handled(self) -> None:
        """Exception objects should be converted to strings."""
        error = ValueError("Invalid value provided")
        result = sanitize_error_message(error)
        assert "Invalid value provided" in result

    def test_home_directory_redacted(self) -> None:
        """Home directory paths should be redacted."""
        msg = "File not found: /home/username/.ssh/id_rsa"
        result = sanitize_error_message(msg)
        assert "/home/" not in result
        assert "[REDACTED]" in result


class TestCreateSafeErrorComment:
    """Test suite for safe error comment creation."""

    def test_basic_error_comment(self) -> None:
        """Basic error comments should be formatted correctly."""
        result = create_safe_error_comment("Connection failed")
        assert result.startswith("❌")
        assert "Connection failed" in result

    def test_error_with_context(self) -> None:
        """Error comments with context should include context."""
        result = create_safe_error_comment("timeout", "GitHub API call")
        assert "GitHub API call" in result
        assert "timeout" in result
        assert result.startswith("❌")

    def test_sensitive_data_redacted_in_comment(self) -> None:
        """Sensitive data should be redacted in comments."""
        error = "Failed with token ghp_secret123"
        result = create_safe_error_comment(error, "Authentication")
        assert "ghp_" not in result
        assert "[REDACTED]" in result
        assert "Authentication" in result
