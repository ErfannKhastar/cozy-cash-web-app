from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.schemas import budgets as budget_schemas
from src.app.crud import budgets as crud_budgets
from src.app.api import deps
from src.app.models.users import Users


router = APIRouter()


@router.get("/", response_model=List[budget_schemas.BudgetResponse])
def read_budgets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    return crud_budgets.get_budgets(db, user_id=current_user.id, skip=skip, limit=limit)


@router.post(
    "/",
    response_model=budget_schemas.BudgetResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_budget(
    budget_in: budget_schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    # چک کنیم که بودجه تکراری برای این ماه و دسته وجود نداشته باشه
    existing_budget = crud_budgets.get_budget_by_category(
        db, user_id=current_user.id, category=budget_in.category, month=budget_in.month
    )
    if existing_budget:
        raise HTTPException(
            status_code=400, detail="Budget for this category and month already exists"
        )

    return crud_budgets.create_budget(db, budget=budget_in, user_id=current_user.id)


@router.put("/{budget_id}", response_model=budget_schemas.BudgetResponse)
def update_budget(
    budget_id: int,
    budget_in: budget_schemas.BudgetCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    budget = crud_budgets.update_budget(
        db, budget_id=budget_id, budget_data=budget_in, user_id=current_user.id
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    budget = crud_budgets.delete_budget(
        db, budget_id=budget_id, user_id=current_user.id
    )
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
