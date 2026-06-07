"""
Budget Schemas.

This module defines the data structures for Budget operations.
It includes validation logic to ensure budget dates are always normalized
to the first day of the month.
"""

from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from decimal import Decimal


class BudgetBase(BaseModel):
    """
    Shared properties for Budget models.
    """

    category: str
    amount: Decimal
    month: date

    @field_validator("month")
    @classmethod
    def standardize_month_to_first_day(cls, v: date) -> date:
        """
        Validator to force the budget date to the first day of the month.
        Example: 2024-05-25 -> 2024-05-01.
        """
        return v.replace(day=1)


class BudgetCreate(BudgetBase):
    """
    Schema for creating a new budget (Same as Base).
    """

    pass


class BudgetResponse(BudgetBase):
    """
    Schema for reading budget data (Includes ID and User ID).
    """

    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
