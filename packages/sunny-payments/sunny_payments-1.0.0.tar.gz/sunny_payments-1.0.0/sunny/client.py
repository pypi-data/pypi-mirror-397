"""
Sunny Payments SDK - Main Client
The primary interface for interacting with Sunny Payments API
"""

from typing import Optional, Any, Dict
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from sunny.exceptions import (
    AuthenticationError,
    APIError,
    NetworkError,
    RateLimitError,
)
from sunny.resources.payments import PaymentsResource
from sunny.resources.customers import CustomersResource
from sunny.resources.refunds import RefundsResource
from sunny.resources.webhooks import WebhooksResource
from sunny.resources.bills import BillsResource
from sunny.resources.crypto import CryptoResource
from sunny.resources.mobile_money import MobileMoneyResource
from sunny.resources.invoices import InvoicesResource
from sunny.resources.qr_codes import QRCodesResource
from sunny.resources.virtual_accounts import VirtualAccountsResource
from sunny.resources.bnpl import BNPLResource

import os

DEFAULT_BASE_URL = os.environ.get("SUNNY_API_URL", "https://api.sunnypay.co.ke/v1")
DEFAULT_TIMEOUT = 30


class Sunny:
    """
    Sunny Payments API client.
    
    Args:
        api_key: Your Sunny API key (starts with sk_live_ or sk_test_)
        base_url: Optional custom API base URL
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum retry attempts for failed requests (default: 3)
    
    Example:
        >>> sunny = Sunny("sk_live_your_api_key")
        >>> payment = sunny.payments.create(
        ...     amount=1000,
        ...     currency="KES",
        ...     source="mpesa"
        ... )
    """

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 3,
    ):
        if not api_key:
            raise AuthenticationError("API key is required")
        
        if not api_key.startswith("sk_"):
            raise AuthenticationError(
                "Invalid API key format. Must start with sk_live_ or sk_test_"
            )

        self._api_key = api_key
        self._base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self._timeout = timeout

        # Create session with retry logic
        self._session = self._create_session(max_retries)

        # Initialize resources
        self.payments = PaymentsResource(self)
        self.customers = CustomersResource(self)
        self.refunds = RefundsResource(self)
        self.webhooks = WebhooksResource(self)
        self.bills = BillsResource(self)
        self.crypto = CryptoResource(self)
        self.mobile_money = MobileMoneyResource(self)
        self.invoices = InvoicesResource(self)
        self.qr_codes = QRCodesResource(self)
        self.virtual_accounts = VirtualAccountsResource(self)
        self.bnpl = BNPLResource(self)

    def _create_session(self, max_retries: int) -> requests.Session:
        """Create a requests session with retry configuration."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
            backoff_factor=0.5,
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "User-Agent": "sunny-python/1.0.0",
        })
        
        return session

    def request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Make a request to the Sunny API.
        
        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API endpoint path
            data: Request body data
            params: Query parameters
            
        Returns:
            API response data
            
        Raises:
            AuthenticationError: If API key is invalid
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
            NetworkError: If network request fails
        """
        url = f"{self._base_url}{path}"

        try:
            response = self._session.request(
                method=method,
                url=url,
                json=data,
                params=params,
                timeout=self._timeout,
            )
        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Unable to connect to Sunny API: {e}")
        except requests.exceptions.Timeout:
            raise NetworkError("Request timed out")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Network error: {e}")

        return self._handle_response(response)

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle API response and raise appropriate errors."""
        if response.status_code >= 200 and response.status_code < 300:
            if response.content:
                return response.json()
            return None

        # Handle errors
        try:
            error_data = response.json()
            message = error_data.get("message") or error_data.get("error") or "An error occurred"
            code = error_data.get("code")
        except ValueError:
            message = response.text or "An error occurred"
            code = None

        if response.status_code == 401:
            raise AuthenticationError(message)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(int(retry_after) if retry_after else None)
        else:
            raise APIError(message, response.status_code, code)
