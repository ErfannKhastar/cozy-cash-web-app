from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date
from decimal import Decimal


class BudgetBase(BaseModel):
    category: str
    amount: Decimal
    month: date

    @field_validator("month")
    @classmethod
    def standardize_month_to_first_day(cls, v: date) -> date:
        return v.replace(day=1)


class BudgetCreate(BudgetBase):
    pass


class BudgetResponse(BudgetBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)
