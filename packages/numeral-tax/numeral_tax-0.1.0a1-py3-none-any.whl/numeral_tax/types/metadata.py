# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["Metadata"]


class Metadata(BaseModel):
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is accepted.
    """

    example_key: Optional[str] = None
    """
    Storing things like an order number may be useful for reporting and
    reconciliation.
    """
