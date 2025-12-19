"""
Sunny Payments SDK - Bills Resource
Handle bill payments: airtime, data, electricity, utilities
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, List

if TYPE_CHECKING:
    from sunny.client import Sunny

from sunny.types import BillTransaction, DataBundle, BillNetwork


class BillsResource:
    """Handle bill payments (airtime, data, electricity, utilities)."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def get_fees(self) -> Dict[str, Any]:
        """
        Get the fee structure for bill payments.
        
        Returns:
            Fee structure by bill type
        """
        return self._client.request("GET", "/bills/fees")

    def calculate_fees(
        self,
        amount: int,
        bill_type: str,
        merchant_tier: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Calculate fees for a specific transaction.
        
        Args:
            amount: Transaction amount
            bill_type: Type of bill (airtime, data, electricity, utility)
            merchant_tier: Optional merchant tier
            
        Returns:
            Fee breakdown
        """
        data = {"amount": amount, "billType": bill_type}
        if merchant_tier:
            data["merchantTier"] = merchant_tier

        response = self._client.request("POST", "/bills/fees/calculate", data=data)
        return response.get("data", response)

    # ============ Airtime ============

    def purchase_airtime(
        self,
        phone_number: str,
        amount: int,
        network: Optional[BillNetwork] = None,
    ) -> BillTransaction:
        """
        Purchase airtime for a phone number.
        
        Args:
            phone_number: Phone number to top up (e.g., "+254712345678")
            amount: Airtime amount
            network: Optional network (safaricom, airtel, telkom)
            
        Returns:
            Transaction details
        """
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "amount": amount,
        }
        if network:
            data["network"] = network

        response = self._client.request("POST", "/bills/airtime", data=data)
        return response.get("data", response)

    # ============ Data Bundles ============

    def get_data_bundles(self, network: Optional[BillNetwork] = None) -> List[DataBundle]:
        """
        Get available data bundles.
        
        Args:
            network: Optional network filter
            
        Returns:
            List of available bundles
        """
        params = {"network": network} if network else None
        response = self._client.request("GET", "/bills/data/bundles", params=params)
        return response.get("data", response)

    def purchase_data(
        self,
        phone_number: str,
        bundle_id: str,
        network: Optional[BillNetwork] = None,
    ) -> BillTransaction:
        """
        Purchase a data bundle.
        
        Args:
            phone_number: Phone number to apply bundle to
            bundle_id: ID of the bundle to purchase
            network: Optional network
            
        Returns:
            Transaction details
        """
        data: Dict[str, Any] = {
            "phoneNumber": phone_number,
            "bundleId": bundle_id,
        }
        if network:
            data["network"] = network

        response = self._client.request("POST", "/bills/data", data=data)
        return response.get("data", response)

    # ============ Electricity ============

    def validate_meter(self, meter_number: str) -> Dict[str, Any]:
        """
        Validate a KPLC meter number.
        
        Args:
            meter_number: The meter number to validate
            
        Returns:
            Meter details including customer name
        """
        data = {"meterNumber": meter_number}
        response = self._client.request("POST", "/bills/electricity/validate", data=data)
        return response.get("data", response)

    def purchase_electricity(
        self,
        meter_number: str,
        amount: int,
        phone_number: Optional[str] = None,
        type: str = "prepaid",
    ) -> BillTransaction:
        """
        Purchase electricity tokens.
        
        Args:
            meter_number: KPLC meter number
            amount: Purchase amount
            phone_number: Phone number for SMS confirmation
            type: "prepaid" or "postpaid"
            
        Returns:
            Transaction with token
        """
        data: Dict[str, Any] = {
            "meterNumber": meter_number,
            "amount": amount,
        }
        if phone_number:
            data["phoneNumber"] = phone_number

        endpoint = "/bills/electricity/postpaid" if type == "postpaid" else "/bills/electricity/prepaid"
        response = self._client.request("POST", endpoint, data=data)
        return response.get("data", response)

    # ============ Utility Bills ============

    def get_providers(self) -> List[Dict[str, Any]]:
        """
        Get list of supported bill providers.
        
        Returns:
            List of providers/billers
        """
        response = self._client.request("GET", "/bills/providers")
        return response.get("data", response)

    def pay_utility(
        self,
        provider_id: str,
        account_number: str,
        amount: int,
    ) -> BillTransaction:
        """
        Pay a utility bill.
        
        Args:
            provider_id: The biller/provider ID
            account_number: Customer account number
            amount: Payment amount
            
        Returns:
            Transaction details
        """
        data = {
            "providerId": provider_id,
            "accountNumber": account_number,
            "amount": amount,
        }
        response = self._client.request("POST", "/bills/utility", data=data)
        return response.get("data", response)
