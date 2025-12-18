# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["UserTokenResponse"]


class UserTokenResponse(BaseModel):
    """Response when token has been created successfully"""

    token: Optional[str] = None
    """The created token."""
