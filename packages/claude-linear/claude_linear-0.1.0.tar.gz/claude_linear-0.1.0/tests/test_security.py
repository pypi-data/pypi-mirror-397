"""Tests for webhook security verification."""

import time
from collections.abc import Callable

import pytest
from fastapi import HTTPException

from src.security import verify_linear_webhook


class TestWebhookSignatureVerification:
    """Test suite for webhook signature verification."""

    def test_valid_signature_accepted(
        self,
        webhook_secret: str,
        valid_webhook_body: bytes,
        create_signature: Callable[[bytes, str], str],
    ) -> None:
        """Valid signatures should be accepted."""
        signature = create_signature(valid_webhook_body, webhook_secret)

        # Extract timestamp from body
        import json

        body_data = json.loads(valid_webhook_body)
        ts = body_data["webhookTimestamp"]

        # Should not raise
        verify_linear_webhook(
            raw_body=valid_webhook_body,
            header_sig_hex=signature,
            secret=webhook_secret,
            webhook_ts_ms=ts,
        )

    def test_invalid_signature_rejected(
        self,
        webhook_secret: str,
        valid_webhook_body: bytes,
    ) -> None:
        """Invalid signatures should be rejected with 401."""
        wrong_signature = "0" * 64  # Wrong signature

        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=valid_webhook_body,
                header_sig_hex=wrong_signature,
                secret=webhook_secret,
                webhook_ts_ms=int(time.time() * 1000),
            )

        assert exc_info.value.status_code == 401
        assert "Invalid signature" in str(exc_info.value.detail)

    def test_missing_signature_rejected(
        self,
        webhook_secret: str,
        valid_webhook_body: bytes,
    ) -> None:
        """Missing signature header should be rejected with 401."""
        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=valid_webhook_body,
                header_sig_hex=None,
                secret=webhook_secret,
                webhook_ts_ms=int(time.time() * 1000),
            )

        assert exc_info.value.status_code == 401
        assert "Missing Linear-Signature" in str(exc_info.value.detail)

    def test_malformed_signature_rejected(
        self,
        webhook_secret: str,
        valid_webhook_body: bytes,
    ) -> None:
        """Malformed signature (not hex) should be rejected with 401."""
        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=valid_webhook_body,
                header_sig_hex="not-valid-hex-gg",
                secret=webhook_secret,
                webhook_ts_ms=int(time.time() * 1000),
            )

        assert exc_info.value.status_code == 401
        assert "Invalid Linear-Signature encoding" in str(exc_info.value.detail)

    def test_missing_timestamp_rejected(
        self,
        webhook_secret: str,
        valid_webhook_body: bytes,
        create_signature: Callable[[bytes, str], str],
    ) -> None:
        """Missing webhook timestamp should be rejected with 401."""
        signature = create_signature(valid_webhook_body, webhook_secret)

        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=valid_webhook_body,
                header_sig_hex=signature,
                secret=webhook_secret,
                webhook_ts_ms=None,
            )

        assert exc_info.value.status_code == 401
        assert "Missing webhookTimestamp" in str(exc_info.value.detail)

    def test_old_timestamp_rejected(
        self,
        webhook_secret: str,
        create_signature: Callable[[bytes, str], str],
    ) -> None:
        """Old timestamps (> 60s) should be rejected."""
        # Create body with old timestamp (2 minutes ago)
        old_ts = int((time.time() - 120) * 1000)
        body = f'{{"action":"update","webhookTimestamp":{old_ts}}}'.encode()
        signature = create_signature(body, webhook_secret)

        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=body,
                header_sig_hex=signature,
                secret=webhook_secret,
                webhook_ts_ms=old_ts,
            )

        assert exc_info.value.status_code == 401
        assert "too old/new" in str(exc_info.value.detail)

    def test_future_timestamp_rejected(
        self,
        webhook_secret: str,
        create_signature: Callable[[bytes, str], str],
    ) -> None:
        """Future timestamps (> 60s) should be rejected."""
        # Create body with future timestamp (2 minutes from now)
        future_ts = int((time.time() + 120) * 1000)
        body = f'{{"action":"update","webhookTimestamp":{future_ts}}}'.encode()
        signature = create_signature(body, webhook_secret)

        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=body,
                header_sig_hex=signature,
                secret=webhook_secret,
                webhook_ts_ms=future_ts,
            )

        assert exc_info.value.status_code == 401
        assert "too old/new" in str(exc_info.value.detail)

    def test_wrong_secret_rejected(
        self,
        valid_webhook_body: bytes,
        create_signature: Callable[[bytes, str], str],
    ) -> None:
        """Signature created with wrong secret should be rejected."""
        # Sign with one secret
        signature = create_signature(valid_webhook_body, "secret-a")

        # Verify with different secret
        with pytest.raises(HTTPException) as exc_info:
            verify_linear_webhook(
                raw_body=valid_webhook_body,
                header_sig_hex=signature,
                secret="secret-b",
                webhook_ts_ms=int(time.time() * 1000),
            )

        assert exc_info.value.status_code == 401
