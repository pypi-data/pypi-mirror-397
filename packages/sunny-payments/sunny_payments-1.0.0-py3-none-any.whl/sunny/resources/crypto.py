"""
Sunny Payments SDK - Crypto Resource
Handle cryptocurrency payments (BTC, ETH, USDT, USDC)
"""

from typing import TYPE_CHECKING, Optional, Dict, Any, Literal

if TYPE_CHECKING:
    from sunny.client import Sunny

CryptoCurrency = Literal["BTC", "ETH", "USDT", "USDC"]


class CryptoResource:
    """Handle cryptocurrency payment operations."""

    def __init__(self, client: "Sunny"):
        self._client = client

    def get_rates(self) -> Dict[str, Any]:
        """
        Get current cryptocurrency exchange rates.
        
        Returns:
            Exchange rates for all supported cryptocurrencies
        """
        return self._client.request("GET", "/crypto/rates")

    def create_address(
        self,
        currency: CryptoCurrency,
        amount: float,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a deposit address for crypto payment.
        
        Args:
            currency: Cryptocurrency type (BTC, ETH, USDT, USDC)
            amount: Amount in USD
            metadata: Optional metadata
            
        Returns:
            Deposit address with QR code
        """
        data: Dict[str, Any] = {"currency": currency, "amount": amount}
        if metadata:
            data["metadata"] = metadata
        return self._client.request("POST", "/crypto/address", data=data)

    def get_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Get crypto payment status.
        
        Args:
            payment_id: The payment ID
            
        Returns:
            Payment status and details
        """
        return self._client.request("GET", f"/crypto/payment/{payment_id}")

    def get_quote(self, amount: float, currency: CryptoCurrency) -> Dict[str, Any]:
        """
        Get a quote for crypto payment.
        
        Args:
            amount: Amount in USD
            currency: Cryptocurrency type
            
        Returns:
            Quote with crypto amount needed
        """
        return self._client.request("POST", "/crypto/quote", data={"amount": amount, "currency": currency})

    def get_stats(self) -> Dict[str, Any]:
        """Get crypto payment statistics."""
        return self._client.request("GET", "/crypto/stats")
