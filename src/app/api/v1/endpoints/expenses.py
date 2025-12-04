from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.schemas import expenses as expense_schemas
from src.app.crud import expenses as crud_expenses
from src.app.api import deps
from src.app.models.users import Users


router = APIRouter()


@router.get("/", response_model=List[expense_schemas.ExpenseResponse])
def read_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    return crud_expenses.get_expenses(
        db, user_id=current_user.id, skip=skip, limit=limit
    )


@router.post(
    "/",
    response_model=expense_schemas.ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    expense_in: expense_schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    return crud_expenses.create_expense(db, expense=expense_in, user_id=current_user.id)


@router.put("/{expense_id}", response_model=expense_schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_in: expense_schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    expense = crud_expenses.update_expense(
        db, expense_id=expense_id, expense_data=expense_in, user_id=current_user.id
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    expense = crud_expenses.delete_expense(
        db, expense_id=expense_id, user_id=current_user.id
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
