# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from ..._models import BaseModel
from ..metadata import Metadata

__all__ = ["CalculationResponse", "AddressUsed", "Customer", "LineItem", "LineItemProduct", "LineItemTaxJurisdiction"]


class AddressUsed(BaseModel):
    """The actual address used for tax calculation after resolution.

    Available with API version 2025-05-12 only.
    """

    address_city: str

    address_country: str

    address_line_1: str

    address_postal_code: str

    address_province: str

    address_line_2: Optional[str] = None


class Customer(BaseModel):
    """Customer information returned in the response.

    Available with API version 2025-05-12.
    """

    type: Optional[Literal["CONSUMER", "BUSINESS"]] = None
    """The type of customer.

    Available with API version 2025-05-12. CONSUMER are private individuals who are
    not registered for VAT/GST (or any other local indirect-tax scheme) in the
    country where the supply is taxed. BUSINESS are companies, sole-proprietors, or
    other legal entities registered for VAT/GST (or an equivalent local tax) in the
    country where the supply is taxed. Defaults to CONSUMER if omitted.
    """


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


class CalculationResponse(BaseModel):
    id: Optional[str] = None
    """The ID of the `calculation`. You will use this to create a `transaction`."""

    address_resolution_status: Optional[Literal["EXACT", "POSTAL_FALLBACK_1", "POSTAL_ONLY"]] = None
    """Status of address resolution for the customer address.

    Available with API version 2025-05-12 only. `EXACT`: exact address match found,
    `POSTAL_FALLBACK_1`: used postal code fallback, `POSTAL_ONLY`: only postal code
    was used for tax calculation.
    """

    address_used: Optional[AddressUsed] = None
    """The actual address used for tax calculation after resolution.

    Available with API version 2025-05-12 only.
    """

    automatic_tax: Optional[Literal["auto", "disabled"]] = None
    """The automatic tax setting for this calculation.

    Available with API version 2025-05-12.
    """

    customer: Optional[Customer] = None
    """Customer information returned in the response.

    Available with API version 2025-05-12.
    """

    customer_currency_code: Optional[str] = None
    """The ISO-4217 currency code of the transaction."""

    expires_at: Optional[float] = None
    """Epoch datetime representing the date and time the tax rates are valid until."""

    line_items: Optional[List[LineItem]] = None

    metadata: Optional[Metadata] = None
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is
    accepted.
    """

    object: Optional[str] = None
    """The type of object: `tax.calculation`."""

    tax_included_in_amount: Optional[bool] = None

    testmode: Optional[bool] = None
    """`True` if using a production API key. `False` if using a test API key."""

    total_amount_excluding_tax: Optional[float] = None
    """Total sale charge, excluding tax."""

    total_amount_including_tax: Optional[float] = None
    """Total sale charge plus tax. What you should charge your customer."""

    total_tax_amount: Optional[float] = None
    """Total tax to charge on this `calculation`."""
