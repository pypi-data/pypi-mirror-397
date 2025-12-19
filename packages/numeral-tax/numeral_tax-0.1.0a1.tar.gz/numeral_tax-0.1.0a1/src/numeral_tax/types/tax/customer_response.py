# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["CustomerResponse"]


class CustomerResponse(BaseModel):
    id: Optional[str] = None
    """The ID of the customer"""

    email: Optional[str] = None
    """The email of the created customer"""

    is_tax_exempt: Optional[bool] = None
    """
    If true, all `POST /tax/calculations` sold to this customer will return $0 in
    tax owed. The default value is `false`.
    """

    name: Optional[str] = None
    """The name of the created customer"""

    object: Optional[str] = None
    """The type of object: `tax.customer`"""

    reference_customer_id: Optional[str] = None
    """The ID of the customer in your system"""
