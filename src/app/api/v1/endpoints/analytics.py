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
    if month and not year:
        year = datetime.now().year

    results = crud_analytics.get_daily_spending(db, current_user.id, month, year)
    data_list = [{"date": str(r.day), "amount": r.total} for r in results]

    return {"data": data_list}
