"""
Sunny Payments Python SDK
Official SDK for integrating Sunny Payment Gateway
"""

from sunny.client import Sunny
from sunny.exceptions import (
    SunnyError,
    AuthenticationError,
    ValidationError,
    APIError,
    NetworkError,
    NotFoundError,
    RateLimitError,
)

__version__ = "1.0.0"
__all__ = [
    "Sunny",
    "SunnyError",
    "AuthenticationError",
    "ValidationError",
    "APIError",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
]
