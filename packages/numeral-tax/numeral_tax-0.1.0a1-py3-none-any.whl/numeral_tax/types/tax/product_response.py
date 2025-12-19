# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ProductResponse"]


class ProductResponse(BaseModel):
    created_at: Optional[float] = None
    """Epoch datetime representing the date and time the product was created"""

    object: Optional[str] = None
    """The type of object: `tax.product`."""

    product_category: Optional[str] = None
    """The category of the created product"""

    reference_product_id: Optional[str] = None
    """The ID of the created product"""

    reference_product_name: Optional[str] = None
    """The name of the created product"""

    testmode: Optional[bool] = None
    """`True` if using a production API key. `False` if using a test API key."""

    updated_at: Optional[float] = None
    """Epoch datetime representing the date and time the product was last updated"""
