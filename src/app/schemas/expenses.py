"""
Expense Schemas.

This module defines the Pydantic models for Expense operations.
It handles data validation for monetary amounts (Decimal) and dates.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ExpenseBase(BaseModel):
    """
    Shared properties for Expense models (Amount, Description, Category).
    """

    amount: Decimal
    description: str
    category: str


class ExpenseCreate(ExpenseBase):
    """
    Schema for creating a new expense.
    Date is Optional. If not provided, DB uses server default (now).
    """

    date: Optional[datetime] = None
    pass


class ExpenseResponse(ExpenseBase):
    """
    Schema for reading expense data (Includes IDs and timestamp).
    """

    id: int
    user_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
