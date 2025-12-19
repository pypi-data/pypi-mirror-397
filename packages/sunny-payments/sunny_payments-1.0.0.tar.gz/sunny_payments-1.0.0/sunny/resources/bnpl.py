"""
Sunny Payments SDK - BNPL (Buy Now Pay Later) Resource
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    from sunny.client import Sunny


class BNPLResource:
    """Handle Buy Now Pay Later operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def check_eligibility(self, customer_id: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """
        Check customer eligibility for BNPL.
        
        Args:
            customer_id: Customer ID
            amount: Optional amount to check eligibility for
            
        Returns:
            Eligibility status and available terms
        """
        data: Dict[str, Any] = {"customer": customer_id}
        if amount:
            data["amount"] = amount
        return self._client.request("POST", "/bnpl/eligibility", data=data)

    def create(
        self,
        customer: str,
        amount: int,
        installments: int,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create a new BNPL plan.
        
        Args:
            customer: Customer ID
            amount: Total amount
            installments: Number of installments (3, 6, or 12)
            description: Plan description
            order_id: Associated order ID
            metadata: Optional metadata
        """
        data: Dict[str, Any] = {
            "customer": customer,
            "amount": amount,
            "installments": installments,
        }
        if description:
            data["description"] = description
        if order_id:
            data["orderId"] = order_id
        if metadata:
            data["metadata"] = metadata
        return self._client.request("POST", "/bnpl/plans", data=data)

    def retrieve(self, plan_id: str) -> Dict[str, Any]:
        """Retrieve a BNPL plan by ID."""
        return self._client.request("GET", f"/bnpl/plans/{plan_id}")

    def list(
        self,
        customer: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List all BNPL plans."""
        params: Dict[str, Any] = {}
        if customer:
            params["customer"] = customer
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._client.request("GET", "/bnpl/plans", params=params)

    def get_installments(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get installments for a plan."""
        return self._client.request("GET", f"/bnpl/plans/{plan_id}/installments")

    def pay_installment(
        self,
        plan_id: str,
        installment_id: str,
        payment_method: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Pay an installment."""
        data = {"paymentMethod": payment_method} if payment_method else {}
        return self._client.request(
            "POST", f"/bnpl/plans/{plan_id}/installments/{installment_id}/pay", data=data
        )

    def cancel(self, plan_id: str) -> Dict[str, Any]:
        """Cancel a BNPL plan."""
        return self._client.request("POST", f"/bnpl/plans/{plan_id}/cancel")

    def get_terms(self) -> Dict[str, Any]:
        """Get BNPL terms and conditions."""
        return self._client.request("GET", "/bnpl/terms")
