# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from datetime import datetime
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["TaxPingResponse"]


class TaxPingResponse(BaseModel):
    """
    Health check response containing status, environment, timestamp, and API version information
    """

    api_version: Literal["2024-09-01", "2025-05-12"]
    """API version from X-API-Version header, or falls back to 2024-09-01"""

    env: Literal["test", "prod"]
    """
    Environment indicator based on API key type: 'test' for testmode keys, 'prod'
    for production keys
    """

    status: Literal["ok"]
    """Always returns 'ok' for successful health checks"""

    timestamp: datetime
    """Current ISO 8601 timestamp when the request was processed"""
