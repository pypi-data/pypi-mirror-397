"""
Sunny Payments SDK - Invoices Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    from sunny.client import Sunny


class InvoicesResource:
    """Handle invoice operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def create(
        self,
        customer: str,
        items: List[Dict[str, Any]],
        currency: str = "KES",
        due_date: Optional[str] = None,
        notes: Optional[str] = None,
        auto_send: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new invoice."""
        data: Dict[str, Any] = {
            "customer": customer,
            "items": items,
            "currency": currency,
        }
        if due_date:
            data["dueDate"] = due_date
        if notes:
            data["notes"] = notes
        if auto_send:
            data["autoSend"] = auto_send
        if metadata:
            data["metadata"] = metadata
        return self._client.request("POST", "/invoices", data=data)

    def retrieve(self, invoice_id: str) -> Dict[str, Any]:
        """Retrieve an invoice by ID."""
        return self._client.request("GET", f"/invoices/{invoice_id}")

    def list(
        self,
        customer: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all invoices."""
        params: Dict[str, Any] = {}
        if customer:
            params["customer"] = customer
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._client.request("GET", "/invoices", params=params)

    def send(self, invoice_id: str) -> Dict[str, Any]:
        """Send an invoice to the customer."""
        return self._client.request("POST", f"/invoices/{invoice_id}/send")

    def mark_paid(self, invoice_id: str, payment_id: Optional[str] = None) -> Dict[str, Any]:
        """Mark invoice as paid."""
        data = {"paymentId": payment_id} if payment_id else {}
        return self._client.request("POST", f"/invoices/{invoice_id}/pay", data=data)

    def cancel(self, invoice_id: str) -> Dict[str, Any]:
        """Cancel an invoice."""
        return self._client.request("POST", f"/invoices/{invoice_id}/cancel")

    def get_pdf_url(self, invoice_id: str) -> Dict[str, Any]:
        """Get invoice PDF download URL."""
        return self._client.request("GET", f"/invoices/{invoice_id}/pdf")
