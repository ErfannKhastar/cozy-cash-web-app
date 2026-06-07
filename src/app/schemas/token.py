"""
Authentication Token Schemas.

This module defines the structure of the JWT tokens used for authentication response
and internal token data handling.
"""

from typing import Optional
from pydantic import BaseModel


class Token(BaseModel):
    """
    Schema for the access token response returned to the client upon login.
    """

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema for the data embedded within the JWT token (payload).
    """

    id: Optional[int] = None
