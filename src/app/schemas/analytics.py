from pydantic import BaseModel, ConfigDict, field_validator
from typing import List


class DashboardSummary(BaseModel):
    total_spent: float
    total_budget: float
    remaining_budget: float
    top_category: str
    status: str


class CategoryData(BaseModel):
    category: str
    total_amount: float
    percentage: float


class CategoryBreakdownResponse(BaseModel):
    data: List[CategoryData]


class TrendDataPoint(BaseModel):
    date: str
    amount: float


class SpendingTrendResponse(BaseModel):
    data: List[TrendDataPoint]



