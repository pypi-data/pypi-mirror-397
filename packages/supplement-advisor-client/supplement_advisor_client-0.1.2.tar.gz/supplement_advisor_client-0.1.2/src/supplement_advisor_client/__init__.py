"""Supplement Advisor API Client Library.

A simple Python client for the Supplement Advisor API.
"""

from .client import analyze_supplement, health_check
from .errors import (
    SupplementAdvisorError,
    APIError,
    AuthenticationError,
    RateLimitError,
    ServerError,
)

__version__ = "0.1.2"

__all__ = [
    "analyze_supplement",
    "health_check",
    "SupplementAdvisorError",
    "APIError",
    "AuthenticationError",
    "RateLimitError",
    "ServerError",
]

