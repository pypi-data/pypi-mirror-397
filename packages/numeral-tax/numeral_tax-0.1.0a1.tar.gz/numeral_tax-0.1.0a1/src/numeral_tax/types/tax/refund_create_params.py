# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Required, TypedDict

__all__ = ["RefundCreateParams", "LineItem"]


class RefundCreateParams(TypedDict, total=False):
    transaction_id: Required[str]
    """The ID of the `transaction` to refund.

    This is the `transaction_id` returned from the `/transactions` creation
    response.
    """

    type: Required[str]
    """This will be either `'full'` or `'partial'`.

    If `type='partial'`, you must also provide the line item(s) you wish to apply
    refunds against.
    """

    line_items: Iterable[LineItem]
    """If the refund is `type=full`, line items aren't necessary.

    If the refund is `type=partial`, you must provide the line item(s) you wish to
    apply refunds against using a `reference_product_id`.
    """

    refund_processed_at: float
    """Unix timestamp in **seconds** representing the date and time the refund was
    made.

    If not provided, the current date and time will be used.
    """


class LineItem(TypedDict, total=False):
    quantity: float
    """The quantity of this product being refunded."""

    reference_line_item_id: str
    """This **optional** attribute is the ID of the line item from your system.

    It will be used only for reporting.
    """

    reference_product_id: str
    """The ID of the product to apply refunds against.

    We will attempt to find the line item from the original transaction based on
    this `reference_product_id`.
    """

    sales_amount_refunded: float
    """
    The sale amount that was refunded to the customer on this line item, not
    inclusive of tax refunded.
    """

    tax_amount_refunded: float
    """The amount of tax that was refunded to the customer."""
