"""
Financial Analytics and Dashboard Endpoints.

This module aggregates user financial data to provide high-level summaries,
charts, and trends. It calculates total spending, remaining budgets, and
category-wise breakdowns to help users visualize their financial health.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from decimal import Decimal
from src.app.db.session import get_db
from src.app.api import deps
from src.app.models.users import Users
from src.app.crud import analytics as crud_analytics
from src.app.schemas import analytics as analytics_schemas


router = APIRouter()


@router.get("/summary", response_model=analytics_schemas.DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
):
    """
    Provides a high-level summary of the user's financial status.

    Calculates total expenses, total budget, remaining balance, and identifies
    the top spending category for a given month/year.

    Args:
        db (Session): Database session.
        current_user (Users): Authenticated user.
        month (int, optional): Month to filter (1-12). Defaults to current month if None.
        year (int, optional): Year to filter. Defaults to current year if None.

    Returns:
        DashboardSummary: An object containing financial totals and a status indicator (Safe/Warning/Danger).
    """
    if month and not year:
        year = datetime.now().year

    total_spent = crud_analytics.get_total_spent(db, current_user.id, month, year)
    total_budget = crud_analytics.get_total_budget(db, current_user.id, month, year)
    top_category = crud_analytics.get_top_category(db, current_user.id, month, year)

    remaining_budget = total_budget - total_spent

    status = "Safe"
    if remaining_budget < 0:
        status = "Danger"
    elif total_budget > 0 and remaining_budget < (total_budget * Decimal(0.2)):
        status = "Warning"

    return {
        "total_spent": total_spent,
        "total_budget": total_budget,
        "remaining_budget": remaining_budget,
        "top_category": top_category,
        "status": status,
    }


@router.get(
    "/category-breakdown", response_model=analytics_schemas.CategoryBreakdownResponse
)
def get_category_breakdown(
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
):
    """
    Retrieves spending breakdown grouped by category.

    Used for generating pie/doughnut charts. Returns the total amount and
    percentage of total spending for each category.

    Args:
        db (Session): Database session.
        current_user (Users): Authenticated user.
        month (int, optional): Month filter.
        year (int, optional): Year filter.

    Returns:
        CategoryBreakdownResponse: A list of categories sorted by spending amount.
    """
    if month and not year:
        year = datetime.now().year

    results = crud_analytics.get_category_breakdown_data(
        db, current_user.id, month, year
    )
    grand_total = sum(r.total for r in results)

    data_list = []
    for r in results:
        percentage = (r.total / grand_total * 100) if grand_total > 0 else 0
        data_list.append(
            {
                "category": r.category,
                "total_amount": r.total,
                "percentage": round(percentage, 1),
            }
        )

    data_list.sort(key=lambda x: x["total_amount"], reverse=True)
    return {"data": data_list}


@router.get("/spending-trend", response_model=analytics_schemas.SpendingTrendResponse)
def get_spending_trend(
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
    month: Optional[int] = Query(None, ge=1, le=12),
    year: Optional[int] = Query(None, ge=2000, le=2100),
):
    """
    Retrieves daily spending trends for line charts.

    Aggregates expenses by day to show spending patterns over the selected month.

    Args:
        db (Session): Database session.
        current_user (Users): Authenticated user.
        month (int, optional): Month filter.
        year (int, optional): Year filter.

    Returns:
        SpendingTrendResponse: A list of daily spending totals.
    """
    if month and not year:
        year = datetime.now().year

    results = crud_analytics.get_daily_spending(db, current_user.id, month, year)
    data_list = [{"date": str(r.day), "amount": r.total} for r in results]

    return {"data": data_list}
