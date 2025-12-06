"""
Expense Schemas.

This module defines the Pydantic models for Expense operations.
It handles data validation for monetary amounts (Decimal) and dates.
"""

from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


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
    Requires a specific date/time for the transaction.
    """

    date: datetime
    pass


class ExpenseResponse(ExpenseBase):
    """
    Schema for reading expense data (Includes IDs and timestamp).
    """

    id: int
    user_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
