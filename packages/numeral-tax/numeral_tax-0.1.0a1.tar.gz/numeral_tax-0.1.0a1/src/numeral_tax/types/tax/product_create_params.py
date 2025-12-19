# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

__all__ = ["ProductCreateParams"]


class ProductCreateParams(TypedDict, total=False):
    product_category: Required[str]
    """The category of the product"""

    reference_product_id: Required[str]
    """The ID of the product"""

    reference_product_name: Required[str]
    """The name of the product"""
