"""
Sunny Payments SDK - QR Codes Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, Literal

if TYPE_CHECKING:
    from sunny.client import Sunny

QRCodeType = Literal["static", "dynamic"]


class QRCodesResource:
    """Handle QR code payment operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        qr_type: QRCodeType,
        amount: Optional[int] = None,
        currency: str = "KES",
        description: Optional[str] = None,
        expires_at: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new QR code for payments.
        
        Args:
            qr_type: 'static' (reusable) or 'dynamic' (one-time)
            amount: Required for dynamic, optional for static
            currency: Currency code
            description: QR code description
            expires_at: Expiration datetime
            metadata: Optional metadata
        """
        data: Dict[str, Any] = {"type": qr_type, "currency": currency}
        if amount:
            data["amount"] = amount
        if description:
            data["description"] = description
        if expires_at:
            data["expiresAt"] = expires_at
        if metadata:
            data["metadata"] = metadata
        return self._client.request("POST", "/qr-codes", data=data)

    def retrieve(self, qr_code_id: str) -> Dict[str, Any]:
        """Retrieve a QR code by ID."""
        return self._client.request("GET", f"/qr-codes/{qr_code_id}")

    def list(
        self,
        qr_type: Optional[QRCodeType] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all QR codes."""
        params: Dict[str, Any] = {}
        if qr_type:
            params["type"] = qr_type
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._client.request("GET", "/qr-codes", params=params)

    def deactivate(self, qr_code_id: str) -> Dict[str, Any]:
        """Deactivate a QR code."""
        return self._client.request("POST", f"/qr-codes/{qr_code_id}/deactivate")

    def get_payments(self, qr_code_id: str) -> Dict[str, Any]:
        """Get payments made via a QR code."""
        return self._client.request("GET", f"/qr-codes/{qr_code_id}/payments")

    def initiate_payment(
        self,
        qr_code_id: str,
        payment_method: str,
        amount: Optional[int] = None,
        customer_phone: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate payment via QR code scan."""
        data: Dict[str, Any] = {"paymentMethod": payment_method}
        if amount:
            data["amount"] = amount
        if customer_phone:
            data["customerPhone"] = customer_phone
        return self._client.request("POST", f"/qr-checkout/{qr_code_id}/pay", data=data)
