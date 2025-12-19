"""
Sunny Payments SDK - Refunds Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from sunny.client import Sunny

from sunny.types import Refund, ListResponse


class RefundsResource:
    """Handle refund operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        payment: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Refund:
        """
        Create a refund for a payment.
        
        Args:
            payment: The payment ID to refund
            amount: Optional amount for partial refund
            reason: Optional reason for the refund
            
        Returns:
            The created Refund object
        """
        data: Dict[str, Any] = {"payment": payment}
        if amount is not None:
            data["amount"] = amount
        if reason:
            data["reason"] = reason

        return self._client.request("POST", "/refunds", data=data)

    def retrieve(self, refund_id: str) -> Refund:
        """
        Retrieve a refund by ID.
        
        Args:
            refund_id: The refund ID
            
        Returns:
            The Refund object
        """
        return self._client.request("GET", f"/refunds/{refund_id}")

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        payment: Optional[str] = None,
    ) -> ListResponse:
        """
        List all refunds.
        
        Args:
            limit: Maximum number of refunds to return
            offset: Number of refunds to skip
            payment: Filter by payment ID
            
        Returns:
            ListResponse with refunds data
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if payment:
            params["payment"] = payment

        return self._client.request("GET", "/refunds", params=params)
