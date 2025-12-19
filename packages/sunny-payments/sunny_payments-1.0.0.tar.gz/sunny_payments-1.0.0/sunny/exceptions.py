"""
Sunny Payments SDK - Custom Exceptions
"""

from typing import Optional, Dict, Any


class SunnyError(Exception):
    """Base exception for all Sunny SDK errors"""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class AuthenticationError(SunnyError):
    """Raised when API key is invalid or missing"""

    def __init__(self, message: str = "Invalid API key provided"):
        super().__init__(message, status_code=401, code="authentication_error")


class ValidationError(SunnyError):
    """Raised when request parameters are invalid"""

    def __init__(self, message: str, field: Optional[str] = None):
        details = {"field": field} if field else {}
        super().__init__(message, status_code=400, code="validation_error", details=details)
        self.field = field


class APIError(SunnyError):
    """Raised for general API errors"""

    def __init__(self, message: str, status_code: int, code: Optional[str] = None):
        super().__init__(message, status_code=status_code, code=code or "api_error")


class NetworkError(SunnyError):
    """Raised when network request fails"""

    def __init__(self, message: str = "Network request failed"):
        super().__init__(message, code="network_error")


class NotFoundError(SunnyError):
    """Raised when a resource is not found"""

    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} '{resource_id}' not found"
        super().__init__(message, status_code=404, code="not_found")
        self.resource = resource
        self.resource_id = resource_id


class RateLimitError(SunnyError):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: Optional[int] = None):
        message = "Rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message, status_code=429, code="rate_limit_error")
        self.retry_after = retry_after
