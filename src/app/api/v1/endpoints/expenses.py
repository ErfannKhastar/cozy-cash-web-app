"""
Expense Management Endpoints.

This module provides the API interface for managing user expenses.
It supports Create, Read, Update, and Delete (CRUD) operations, allowing
users to track their spending habits efficiently.
"""

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
    """
    Retrieves a list of expenses for the current user.

    Args:
        skip (int, optional): Number of records to skip for pagination. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.
        db (Session): Database session dependency.
        current_user (Users): The authenticated user.

    Returns:
        List[ExpenseResponse]: A list of expense objects associated with the user.
    """
    if limit > 100:
        limit = 100

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
    """
    Creates a new expense record.

    Args:
        expense_in (ExpenseCreate): The payload containing expense details (amount, category, etc.).
        db (Session): Database session dependency.
        current_user (Users): The authenticated user.

    Returns:
        ExpenseResponse: The created expense object.
    """
    return crud_expenses.create_expense(db, expense=expense_in, user_id=current_user.id)


@router.put("/{expense_id}", response_model=expense_schemas.ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_in: expense_schemas.ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(deps.get_current_user),
):
    """
    Updates an existing expense record.

    Args:
        expense_id (int): The unique ID of the expense to update.
        expense_in (ExpenseCreate): The new data for the expense.
        db (Session): Database session dependency.
        current_user (Users): The authenticated user.

    Returns:
        ExpenseResponse: The updated expense object.

    Raises:
        HTTPException(404): If the expense is not found or does not belong to the user.
    """
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
    """
    Deletes an expense record.

    Args:
        expense_id (int): The unique ID of the expense to delete.
        db (Session): Database session dependency.
        current_user (Users): The authenticated user.

    Returns:
        None: Returns HTTP 204 (No Content) upon successful deletion.

    Raises:
        HTTPException(404): If the expense is not found or does not belong to the user.
    """
    expense = crud_expenses.delete_expense(
        db, expense_id=expense_id, user_id=current_user.id
    )
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
