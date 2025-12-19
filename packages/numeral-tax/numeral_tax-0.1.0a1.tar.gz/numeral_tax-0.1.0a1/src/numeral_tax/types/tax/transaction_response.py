# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from ..metadata import Metadata

__all__ = ["TransactionResponse", "LineItem", "LineItemProduct", "LineItemTaxJurisdiction"]


class LineItemProduct(BaseModel):
    product_tax_code: Optional[str] = None

    reference_line_item_id: Optional[str] = None

    reference_product_id: Optional[str] = None

    reference_product_name: Optional[str] = None


class LineItemTaxJurisdiction(BaseModel):
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


class LineItem(BaseModel):
    amount_excluding_tax: Optional[float] = None

    amount_including_tax: Optional[float] = None

    product: Optional[LineItemProduct] = None

    quantity: Optional[float] = None

    tax_amount: Optional[float] = None

    tax_jurisdictions: Optional[List[Optional[LineItemTaxJurisdiction]]] = None


class TransactionResponse(BaseModel):
    id: Optional[str] = None
    """The ID of the `transaction`.

    We highly recommend you store this value. If you need to refund or query the
    data from this transaction, you will use this ID as a reference.
    """

    calculation_id: Optional[str] = None
    """The ID of the `calculation` that was used to create this transaction"""

    customer_currency_code: Optional[str] = None
    """The ISO-4217 currency code of the transaction"""

    filing_currency_code: Optional[str] = None
    """
    The currency code of the filing that will be used to remit taxes collected on
    this transaction
    """

    line_items: Optional[List[LineItem]] = None

    metadata: Optional[Metadata] = None
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is
    accepted.
    """

    object: Optional[str] = None
    """The type of object: `tax.transaction`."""

    reference_order_id: Optional[str] = None
    """The unique order ID you provided when creating the `transaction`"""

    testmode: Optional[bool] = None
    """`True` if using a production API key.

    If `true`, Numeral will record this `transaction` towards your nexus totals. If
    you're registered and collecting in the relevant jurisdiction, we'll file the
    tax.
    """

    transaction_processed_at: Optional[float] = None
    """Unix timestamp in **seconds** representing the date and time your sale was made.

    If not provided, the date and time this `transaction` was created
    """
