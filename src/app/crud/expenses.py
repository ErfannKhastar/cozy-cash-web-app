"""
CRUD Operations for Expenses.

This module handles database interactions for Expense records.
It includes functions to create, read (list and retrieve single),
update, and delete expenses for specific users.
"""

from typing import List
from sqlalchemy.orm import Session
from src.app.models.expenses import Expenses
from src.app.schemas.expenses import ExpenseCreate


def get_expenses(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Expenses]:
    """
    Retrieves a list of expenses for a specific user with pagination.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user who owns the expenses.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.

    Returns:
        List[Expenses]: A list of expense objects.
    """
    return (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_expense(db: Session, expense: ExpenseCreate, user_id: int):
    """
    Creates a new expense record for a user.

    Args:
        db (Session): The database session.
        expense (ExpenseCreate): The expense data schema.
        user_id (int): The ID of the user creating the expense.

    Returns:
        Expenses: The created expense object.
    """
    db_expense = Expenses(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expense_by_id(db: Session, expense_id: int, user_id: int):
    """
    Retrieves a specific expense by ID, ensuring ownership.

    Args:
        db (Session): The database session.
        expense_id (int): The ID of the expense to retrieve.
        user_id (int): The ID of the user (for security check).

    Returns:
        Expenses | None: The expense object if found and owned by user, otherwise None.
    """
    return (
        db.query(Expenses)
        .filter(Expenses.id == expense_id, Expenses.user_id == user_id)
        .first()
    )


def delete_expense(db: Session, expense_id: int, user_id: int):
    """
    Deletes an expense record if it exists and belongs to the user.

    Args:
        db (Session): The database session.
        expense_id (int): The ID of the expense to delete.
        user_id (int): The ID of the user.

    Returns:
        Expenses | None: The deleted expense object if found, otherwise None.
    """
    expense = (
        db.query(Expenses)
        .filter(Expenses.id == expense_id, Expenses.user_id == user_id)
        .first()
    )
    if expense:
        db.delete(expense)
        db.commit()
    return expense


def update_expense(
    db: Session, expense_id: int, expense_data: ExpenseCreate, user_id: int
):
    """
    Updates an existing expense with new data.

    Only the fields provided in `expense_data` will be updated (partial update).

    Args:
        db (Session): The database session.
        expense_id (int): The ID of the expense to update.
        expense_data (ExpenseCreate): The new data for the expense.
        user_id (int): The ID of the user.

    Returns:
        Expenses | None: The updated expense object, or None if not found.
    """
    db_expense = (
        db.query(Expenses)
        .filter(Expenses.id == expense_id, Expenses.user_id == user_id)
        .first()
    )
    if not db_expense:
        return None

    update_data = expense_data.model_dump(exclude_unset=True)

    if "id" in update_data:
        del update_data["id"]
    if "user_id" in update_data:
        del update_data["user_id"]

    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense
