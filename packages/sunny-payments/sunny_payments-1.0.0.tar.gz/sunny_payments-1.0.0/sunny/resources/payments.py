"""
Sunny Payments SDK - Payments Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from sunny.client import Sunny

from sunny.types import Payment, PaymentCreateParams, ListResponse


class PaymentsResource:
    """
    Handle payment operations.
    
    Example:
        >>> payment = sunny.payments.create(
        ...     amount=1000,
        ...     currency="KES",
        ...     source="mpesa"
        ... )
    """

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        amount: int,
        currency: str,
        source: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        customer: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> Payment:
        """
        Create a new payment.
        
        Args:
            amount: Payment amount in smallest currency unit (e.g., cents)
            currency: Three-letter ISO currency code (e.g., "KES")
            source: Payment source (mpesa, card, bank_transfer, wallet, crypto)
            description: Optional payment description
            metadata: Optional key-value metadata
            customer: Optional customer ID to associate with payment
            idempotency_key: Optional key for idempotent requests
            
        Returns:
            The created Payment object
            
        Example:
            >>> payment = sunny.payments.create(
            ...     amount=5000,
            ...     currency="KES",
            ...     source="mpesa",
            ...     metadata={"order_id": "12345"}
            ... )
        """
        data: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "source": source,
        }
        if description:
            data["description"] = description
        if metadata:
            data["metadata"] = metadata
        if customer:
            data["customer"] = customer
        if idempotency_key:
            data["idempotency_key"] = idempotency_key

        return self._client.request("POST", "/payments", data=data)

    def retrieve(self, payment_id: str) -> Payment:
        """
        Retrieve a payment by ID.
        
        Args:
            payment_id: The payment ID (e.g., "pay_123")
            
        Returns:
            The Payment object
        """
        return self._client.request("GET", f"/payments/{payment_id}")

    def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        status: Optional[str] = None,
        created_after: Optional[str] = None,
        created_before: Optional[str] = None,
    ) -> ListResponse:
        """
        List all payments.
        
        Args:
            limit: Maximum number of payments to return
            offset: Number of payments to skip
            status: Filter by payment status
            created_after: Filter payments created after this date
            created_before: Filter payments created before this date
            
        Returns:
            ListResponse with payments data
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        if offset is not None:
            params["offset"] = offset
        if status:
            params["status"] = status
        if created_after:
            params["created_after"] = created_after
        if created_before:
            params["created_before"] = created_before

        return self._client.request("GET", "/payments", params=params)

    def capture(
        self,
        payment_id: str,
        amount: Optional[int] = None,
    ) -> Payment:
        """
        Capture an authorized payment.
        
        Args:
            payment_id: The payment ID
            amount: Optional amount for partial capture
            
        Returns:
            The updated Payment object
        """
        data = {"amount": amount} if amount else {}
        return self._client.request("POST", f"/payments/{payment_id}/capture", data=data)

    def refund(
        self,
        payment_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> Payment:
        """
        Refund a payment.
        
        Args:
            payment_id: The payment ID
            amount: Optional amount for partial refund
            reason: Optional reason for the refund
            
        Returns:
            The updated Payment object
        """
        data: Dict[str, Any] = {}
        if amount is not None:
            data["amount"] = amount
        if reason:
            data["reason"] = reason

        return self._client.request("POST", f"/payments/{payment_id}/refund", data=data)
