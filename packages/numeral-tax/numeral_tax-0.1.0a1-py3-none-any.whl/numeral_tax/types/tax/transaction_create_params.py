# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..metadata_param import MetadataParam

__all__ = ["TransactionCreateParams"]


class TransactionCreateParams(TypedDict, total=False):
    calculation_id: Required[str]
    """The ID of the `calculation` that you want to record as a sale"""

    reference_order_id: Required[str]
    """The ID of this order in your system.

    Must be unique among all your `transactions`
    """

    metadata: MetadataParam
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is
    accepted.
    """

    transaction_processed_at: float
    """Unix timestamp in **seconds** representing the date and time your sale was made.

    If not provided, the current date and time will be used.
    """
