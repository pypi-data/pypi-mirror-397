"""Webhook signature verification utilities for the Nellie API SDK."""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, Union

from .types import Book

# Maximum allowed time difference (in seconds) between signature timestamp and current time
MAX_SIGNATURE_SKEW_SECONDS: int = 300  # 5 minutes


class WebhookSignatureError(Exception):
    """Raised when the webhook signature verification fails."""

    pass


class Webhook:
    """Utility class for verifying and handling webhook events.

    Example usage:
        >>> from nellie_api import Webhook, WebhookSignatureError
        >>>
        >>> def handle_webhook(request):
        ...     payload = request.body
        ...     sig_header = request.headers.get("X-Nellie-Signature")
        ...     try:
        ...         event = Webhook.construct_event(payload, sig_header, "whsec_...")
        ...         if event.status == "completed":
        ...             print(f"Book ready: {event.result_url}")
        ...     except WebhookSignatureError:
        ...         return "Invalid signature", 400
    """

    @staticmethod
    def construct_event(
        payload: Union[str, bytes], sig_header: str, secret: str
    ) -> Book:
        """
        Verifies the signature and returns the parsed event object.

        Args:
            payload: The raw request body (as string or bytes).
            sig_header: The X-Nellie-Signature header value.
            secret: Your webhook secret (whsec_...).

        Returns:
            Book: The event data wrapped in a Book object.

        Raises:
            WebhookSignatureError: If the signature is invalid or timestamp is stale.
            ValueError: If the payload is invalid JSON.
        """
        if Webhook.verify_signature(payload, sig_header, secret):
            data: Dict[str, Any] = json.loads(payload)
            return Book.from_api_response(data)
        else:
            raise WebhookSignatureError("Invalid webhook signature")

    @staticmethod
    def verify_signature(
        payload: Union[str, bytes], sig_header: str, secret: str
    ) -> bool:
        """
        Verifies that the payload was signed with the given secret.

        Args:
            payload: The raw request body.
            sig_header: The X-Nellie-Signature header value (format: t=...,v1=...).
            secret: Your webhook secret.

        Returns:
            bool: True if signature is valid, False otherwise.
        """
        if not sig_header or not secret:
            return False

        try:
            # 1. Parse header
            parts: Dict[str, str] = dict(
                x.split("=", 1) for x in sig_header.split(",")
            )
            timestamp: Optional[str] = parts.get("t")
            signature: Optional[str] = parts.get("v1")

            if not timestamp or not signature:
                return False

            # Reject replayed events outside the allowed time window
            current_ts: int = int(time.time())
            sent_ts: int = int(timestamp)
            if abs(current_ts - sent_ts) > MAX_SIGNATURE_SKEW_SECONDS:
                return False

            # 2. Normalize payload to bytes
            payload_bytes: bytes
            if isinstance(payload, str):
                payload_bytes = payload.encode("utf-8")
            else:
                payload_bytes = payload

            # 3. Re-create the signed content string
            # The signature is created from "timestamp.payload"
            signed_content: bytes = f"{timestamp}.".encode("utf-8") + payload_bytes

            # 4. Calculate expected hash
            expected: str = hmac.new(
                key=secret.encode("utf-8"),
                msg=signed_content,
                digestmod=hashlib.sha256,
            ).hexdigest()

            # 5. Compare securely
            return hmac.compare_digest(expected, signature)

        except Exception:
            return False

    @staticmethod
    def generate_signature(payload: Union[str, bytes], secret: str) -> str:
        """
        Generate a webhook signature for testing purposes.

        Args:
            payload: The payload to sign.
            secret: The webhook secret.

        Returns:
            str: The signature header value in format "t=...,v1=..."
        """
        timestamp: str = str(int(time.time()))

        payload_bytes: bytes
        if isinstance(payload, str):
            payload_bytes = payload.encode("utf-8")
        else:
            payload_bytes = payload

        signed_content: bytes = f"{timestamp}.".encode("utf-8") + payload_bytes
        signature: str = hmac.new(
            key=secret.encode("utf-8"),
            msg=signed_content,
            digestmod=hashlib.sha256,
        ).hexdigest()

        return f"t={timestamp},v1={signature}"
