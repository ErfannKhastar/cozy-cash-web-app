"""
User Management Schemas.

This module defines the data structures for User operations such as registration,
login, and profile retrieval. It explicitly separates the creation schema (with password)
from the response schema (without password) for security.
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class UserCreate(BaseModel):
    """
    Schema for user registration.
    """

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Schema for returning user profile data.
    WARNING: Never include the 'password' field in this schema.
    """

    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login credentials.
    """

    email: EmailStr
    password: str
