"""
Analytics and Dashboard Schemas.

This module defines the Pydantic models (data transfer objects) used for
returning statistical data to the frontend, such as dashboard summaries,
charts data, and trend analysis.
"""

from pydantic import BaseModel
from typing import List


class DashboardSummary(BaseModel):
    """
    Schema for the high-level dashboard summary cards.
    """

    total_spent: float
    total_budget: float
    remaining_budget: float
    top_category: str
    status: str


class CategoryData(BaseModel):
    """
    Schema for a single category's spending data in charts.
    """

    category: str
    total_amount: float
    percentage: float


class CategoryBreakdownResponse(BaseModel):
    """
    Wrapper schema for the list of category data.
    """

    data: List[CategoryData]


class TrendDataPoint(BaseModel):
    """
    Schema for a single point in the spending trend line chart (Date + Amount).
    """

    date: str
    amount: float


class SpendingTrendResponse(BaseModel):
    """
    Wrapper schema for the spending trend data series.
    """

    data: List[TrendDataPoint]
