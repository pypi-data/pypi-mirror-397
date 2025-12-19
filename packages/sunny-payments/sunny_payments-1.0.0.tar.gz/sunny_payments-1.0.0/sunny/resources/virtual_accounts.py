"""
Sunny Payments SDK - Virtual Accounts Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    from sunny.client import Sunny


class VirtualAccountsResource:
    """Handle virtual bank account operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        customer: Optional[str] = None,
        bank_code: Optional[str] = None,
        account_name: Optional[str] = None,
        expires_at: Optional[str] = None,
        single_use: bool = False,
        expected_amount: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new virtual account."""
        data: Dict[str, Any] = {"singleUse": single_use}
        if customer:
            data["customer"] = customer
        if bank_code:
            data["bankCode"] = bank_code
        if account_name:
            data["accountName"] = account_name
        if expires_at:
            data["expiresAt"] = expires_at
        if expected_amount:
            data["expectedAmount"] = expected_amount
        if metadata:
            data["metadata"] = metadata
        return self._client.request("POST", "/virtual-accounts", data=data)

    def retrieve(self, account_id: str) -> Dict[str, Any]:
        """Retrieve a virtual account by ID."""
        return self._client.request("GET", f"/virtual-accounts/{account_id}")

    def list(
        self,
        customer: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all virtual accounts."""
        params: Dict[str, Any] = {}
        if customer:
            params["customer"] = customer
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._client.request("GET", "/virtual-accounts", params=params)

    def close(self, account_id: str) -> Dict[str, Any]:
        """Close a virtual account."""
        return self._client.request("POST", f"/virtual-accounts/{account_id}/close")

    def get_transactions(self, account_id: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get transactions for a virtual account."""
        params = {"limit": limit} if limit else None
        return self._client.request("GET", f"/virtual-accounts/{account_id}/transactions", params=params)

    def get_supported_banks(self) -> List[Dict[str, str]]:
        """Get supported banks for virtual accounts."""
        return self._client.request("GET", "/virtual-accounts/banks")
