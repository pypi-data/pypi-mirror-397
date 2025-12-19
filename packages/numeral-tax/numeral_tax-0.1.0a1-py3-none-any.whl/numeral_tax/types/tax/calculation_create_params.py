# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._utils import PropertyInfo
from ..metadata_param import MetadataParam

__all__ = [
    "CalculationCreateParams",
    "Customer",
    "CustomerAddress",
    "CustomerTaxID",
    "OrderDetails",
    "OrderDetailsLineItem",
    "OriginAddress",
]


class CalculationCreateParams(TypedDict, total=False):
    customer: Required[Customer]
    """Customer details.

    Address is required. Optionally accepts a customer ID for order tracking and
    exemptions.
    """

    order_details: Required[OrderDetails]

    metadata: MetadataParam
    """You can store arbitrary keys and values in the metadata.

    Any valid JSON object whose values are less than 255 characters long is
    accepted.
    """

    origin_address: OriginAddress
    """The address that a product is shipped from.

    Optional for API version 2024-09-01, required for 2025-05-12.
    """

    x_api_version: Annotated[Literal["2025-05-12", "2024-09-01"], PropertyInfo(alias="X-API-Version")]


class CustomerAddress(TypedDict, total=False):
    address_city: Required[str]

    address_country: Required[str]
    """The country code. Must be a valid ISO 3166-1 alpha-2 country code."""

    address_line_1: Required[str]

    address_postal_code: Required[str]

    address_province: Required[str]
    """The state, province, or region.

    Must be a valid 2 digit ISO 3166-2 subdivision code.
    """

    address_type: Required[str]
    """The type of address. Must be one of: shipping or billing."""

    address_line_2: str


class CustomerTaxID(TypedDict, total=False):
    type: Required[Literal["VAT", "GST", "EIN"]]
    """The type of tax ID."""

    value: Required[str]
    """The tax ID value"""


class Customer(TypedDict, total=False):
    """Customer details.

    Address is required. Optionally accepts a customer ID for order tracking and exemptions.
    """

    address: Required[CustomerAddress]

    id: str
    """The ID of the customer that you created in our system.

    Can be used to log customer information or indicate that a purchaser is tax
    exempt.
    """

    tax_ids: Iterable[CustomerTaxID]
    """Array of tax identification numbers.

    Available with API version 2025-05-12. Only available for BUSINESS customer
    types.
    """

    type: Literal["CONSUMER", "BUSINESS"]
    """The type of customer.

    Available with API version 2025-05-12. CONSUMER are private individuals.
    BUSINESS are companies or legal entities registered for VAT/GST.
    """


class OrderDetailsLineItem(TypedDict, total=False):
    amount: Required[float]
    """The price of this line item in the currency's smallest unit."""

    quantity: Required[float]
    """The quantity of this product being sold."""

    product_category: str
    """A tax category from our category taxonomy. Required if no reference_product_id."""

    reference_line_item_id: str
    """The ID of the line item from your system."""

    reference_product_id: str
    """The product ID used to uniquely reference this product.

    Required if no product_category.
    """


class OrderDetails(TypedDict, total=False):
    customer_currency_code: Required[str]
    """The currency code of the transaction.

    For API version 2024-09-01: Must be either USD or CAD. For API version
    2025-05-12: Supports 32 currencies.
    """

    line_items: Required[Iterable[OrderDetailsLineItem]]
    """Each line item should represent one type of product."""

    tax_included_in_amount: Required[bool]
    """For the line items in this transaction, does the amount include tax?"""

    automatic_tax: Literal["auto", "disabled"]
    """Controls automatic tax behavior. Available with API version 2025-05-12."""


class OriginAddress(TypedDict, total=False):
    """The address that a product is shipped from.

    Optional for API version 2024-09-01, required for 2025-05-12.
    """

    address_city: Required[str]

    address_country: Required[str]
    """The country code. Must be a valid ISO 3166-1 alpha-2 country code."""

    address_line_1: Required[str]

    address_postal_code: Required[str]

    address_province: Required[str]
    """The state, province, or region.

    Must be a valid 2 digit ISO 3166-2 subdivision code.
    """

    address_line_2: str
