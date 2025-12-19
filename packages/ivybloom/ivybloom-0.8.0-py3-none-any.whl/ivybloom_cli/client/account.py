"""
Account-related API helpers.
"""

from __future__ import annotations

from .base import JSONDict


class AccountClientMixin:
    """Mixin providing account endpoints."""

    def get_account_info(self) -> JSONDict:
        """Get account information."""
        return self.get("/account")

    def get_usage_stats(self) -> JSONDict:
        """Get usage statistics."""
        return self.get("/usage")

    def check_cli_linking_status(self, client_id: str) -> JSONDict:
        """Check if CLI client is linked to a user account."""
        return self.get(f"/link-status/{client_id}")

    def verify_cli_linking(self, client_id: str) -> JSONDict:
        """Verify and complete CLI linking process."""
        return self.post(f"/verify-link/{client_id}")

