# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["DeleteProductResponse"]


class DeleteProductResponse(BaseModel):
    deleted_at: Optional[float] = None
    """Epoch datetime representing the date and time the object was deleted"""

    object: Optional[str] = None
    """The type of object deleted"""
