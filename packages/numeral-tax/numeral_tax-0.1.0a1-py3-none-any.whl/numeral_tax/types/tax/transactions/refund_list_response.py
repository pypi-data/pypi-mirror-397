# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ...._models import BaseModel

__all__ = ["RefundListResponse", "Refund", "RefundLineItem", "RefundLineItemProduct", "RefundLineItemTaxJurisdiction"]


class RefundLineItemProduct(BaseModel):
    product_tax_code: Optional[str] = None

    reference_line_item_id: Optional[str] = None

    reference_product_id: Optional[str] = None

    reference_product_name: Optional[str] = None


class RefundLineItemTaxJurisdiction(BaseModel):
    fee_amount: Optional[float] = None
    """The flat fee that is added to this transaction.

    Like all numeric values, this will be returned in cents and should be added
    directly to the tax amount independent of other percentages. For example, a $100
    transaction taxed at 5% and with a `fee_amount: 50` will lead to
    `($100 * 5% + 0.50) = $5.50` in tax being charged
    """

    jurisdiction_name: Optional[str] = None

    note: Optional[str] = None
    """Additional information about the tax jurisdiction.

    Available with API version 2025-05-12. For B2B transactions, reverse charge is
    determined by comparing origin_address.address_country vs
    customer.address.address_country (same country = domestic VAT, different
    countries = reverse charge).
    """

    rate_type: Optional[str] = None

    tax_rate: Optional[float] = None
    """The tax rate percentage applied to this transaction."""


class RefundLineItem(BaseModel):
    amount_excluding_tax: Optional[float] = None
    """The amount excluding tax, which should be a negative number for refunds."""

    amount_including_tax: Optional[float] = None
    """The amount including tax, which should be a negative number for refunds."""

    product: Optional[RefundLineItemProduct] = None

    quantity: Optional[float] = None
    """The quantity of this product being refunded."""

    tax_amount: Optional[float] = None
    """The tax amount, which should be a negative number for refunds."""

    tax_jurisdictions: Optional[List[Optional[RefundLineItemTaxJurisdiction]]] = None


class Refund(BaseModel):
    id: Optional[str] = None
    """The ID of the `refund`"""

    line_items: Optional[List[RefundLineItem]] = None

    object: Optional[str] = None
    """The type of object: `tax.refund`."""

    refund_processed_at: Optional[float] = None
    """Unix timestamp in **seconds** representing the date and time the refund was
    made.

    If not provided, the time the refund was created will be used.
    """

    testmode: Optional[bool] = None
    """`True` if using a production API key. `False` if using a test API key."""


class RefundListResponse(BaseModel):
    refunds: Optional[List[Refund]] = None
