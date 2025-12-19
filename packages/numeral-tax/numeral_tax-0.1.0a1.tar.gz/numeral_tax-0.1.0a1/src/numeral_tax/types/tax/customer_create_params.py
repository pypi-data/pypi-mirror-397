# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["CustomerCreateParams"]


class CustomerCreateParams(TypedDict, total=False):
    email: Required[str]
    """The customer's email"""

    is_tax_exempt: bool
    """
    If true, all `POST /tax/calculations` sold to this customer will return $0 in
    tax owed. The default value is `false`.
    """

    name: str
    """The customer's name"""

    reference_customer_id: str
    """The ID of the customer in your system"""
