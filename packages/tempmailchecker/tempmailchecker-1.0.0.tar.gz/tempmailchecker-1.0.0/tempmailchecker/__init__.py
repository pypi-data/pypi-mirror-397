"""
TempMailChecker Python SDK

Detect disposable email addresses using the TempMailChecker API.
"""

from .client import TempMailChecker, ENDPOINT_EU, ENDPOINT_US, ENDPOINT_ASIA

__version__ = "1.0.0"
__all__ = ["TempMailChecker", "ENDPOINT_EU", "ENDPOINT_US", "ENDPOINT_ASIA"]

