# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .product_response import ProductResponse

__all__ = ["ProductListResponse"]


class ProductListResponse(BaseModel):
    has_more: Optional[bool] = None
    """
    This will be either `true` or `false` depending on if there are more products to
    be returned in the next request.
    """

    last_product_id: Optional[str] = None
    """The ID of the last product returned in the response.

    This can be used as a cursor for pagination.
    """

    products: Optional[List[ProductResponse]] = None
