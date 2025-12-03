from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal


class ExpenseBase(BaseModel):
    amount: Decimal
    description: str
    category: str


class ExpenseCreate(ExpenseBase):
    date: datetime
    pass


class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
