# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import TypedDict

__all__ = ["ProductListParams"]


class ProductListParams(TypedDict, total=False):
    cursor: str
    """The product ID to start pagination from.

    This is the last product ID retrieved from the previous list request. An example
    path looks like `/tax/products?cursor=p-20506`
    """
