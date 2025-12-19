"""
Sunny Payments SDK - Mobile Money Resource
Handle mobile money payments (M-Pesa, MTN MoMo, Airtel Money, Tigo Pesa)
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, Literal

if TYPE_CHECKING:
    from sunny.client import Sunny

MobileMoneyProvider = Literal["mpesa", "mtn", "airtel", "tigo"]


class MobileMoneyResource:
    """Handle mobile money payment operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    # ============ M-Pesa ============

    def mpesa_stk_push(
        self,
        phone_number: str,
        amount: int,
        account_reference: Optional[str] = None,
        transaction_desc: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Initiate M-Pesa STK Push (Lipa Na M-Pesa).
        
        Args:
            phone_number: Customer phone number (e.g., '254712345678')
            amount: Amount to charge
            account_reference: Payment reference
            transaction_desc: Transaction description
            callback_url: Optional callback URL
            
        Returns:
            STK Push response with checkout request ID
        """
        data: Dict[str, Any] = {"phoneNumber": phone_number, "amount": amount}
        if account_reference:
            data["accountReference"] = account_reference
        if transaction_desc:
            data["transactionDesc"] = transaction_desc
        if callback_url:
            data["callbackUrl"] = callback_url
        return self._client.request("POST", "/kenya/mpesa/stk-push", data=data)

    def mpesa_status(self, transaction_id: str) -> Dict[str, Any]:
        """Check M-Pesa transaction status."""
        return self._client.request("GET", f"/kenya/mpesa/status/{transaction_id}")

    def mpesa_b2c(
        self,
        phone_number: str,
        amount: int,
        command_id: str = "BusinessPayment",
        remarks: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        M-Pesa B2C Payment (Business to Customer).
        
        Args:
            phone_number: Recipient phone number
            amount: Amount to send
            command_id: SalaryPayment, BusinessPayment, or PromotionPayment
            remarks: Optional remarks
        """
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "amount": amount,
            "commandID": command_id,
        }
        if remarks:
            data["remarks"] = remarks
        return self._client.request("POST", "/kenya/mpesa/b2c", data=data)

    # ============ MTN MoMo ============

    def mtn_collect(
        self,
        phone_number: str,
        amount: int,
        currency: str,
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate MTN MoMo collection."""
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "amount": amount,
            "currency": currency,
        }
        if reference:
            data["reference"] = reference
        return self._client.request("POST", "/mobile-money/mtn/collect", data=data)

    def mtn_disburse(
        self,
        phone_number: str,
        amount: int,
        currency: str,
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """MTN MoMo disbursement (payout)."""
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "amount": amount,
            "currency": currency,
        }
        if reference:
            data["reference"] = reference
        return self._client.request("POST", "/mobile-money/mtn/disburse", data=data)

    # ============ Airtel Money ============

    def airtel_collect(
        self,
        phone_number: str,
        amount: int,
        currency: str,
        reference: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Initiate Airtel Money collection."""
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "amount": amount,
            "currency": currency,
        }
        if reference:
            data["reference"] = reference
        return self._client.request("POST", "/mobile-money/airtel/collect", data=data)

    # ============ Generic ============

    def get_transaction(self, transaction_id: str) -> Dict[str, Any]:
        """Get mobile money transaction by ID."""
        return self._client.request("GET", f"/mobile-money/transaction/{transaction_id}")

    def list_transactions(
        self,
        provider: Optional[MobileMoneyProvider] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """List mobile money transactions."""
        params: Dict[str, Any] = {}
        if provider:
            params["provider"] = provider
        if status:
            params["status"] = status
        if limit:
            params["limit"] = limit
        return self._client.request("GET", "/mobile-money/transactions", params=params)
