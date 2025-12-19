# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["MetadataParam"]


class MetadataParam(TypedDict, total=False):
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is accepted.
    """

    example_key: str
    """
    Storing things like an order number may be useful for reporting and
    reconciliation.
    """
