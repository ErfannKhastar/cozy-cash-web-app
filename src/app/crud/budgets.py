"""
CRUD Operations for Budgets.

This module manages database interactions for Budget records, including
creating new budgets, retrieving lists or specific budgets by category,
updating existing budgets, and deleting them.
"""

from typing import List
from sqlalchemy.orm import Session
from src.app.models.budgets import Budgets
from src.app.schemas.budgets import BudgetCreate


def get_budgets(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Budgets]:
    """
    Retrieves a list of budgets for a specific user.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        skip (int, optional): Number of records to skip. Defaults to 0.
        limit (int, optional): Maximum number of records to return. Defaults to 100.

    Returns:
        List[Budgets]: A list of budget objects.
    """
    return (
        db.query(Budgets)
        .filter(Budgets.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_budget(db: Session, budget: BudgetCreate, user_id: int):
    """
    Creates a new budget record for a user.
    Forces the budget date to be the first day of the month.

    Args:
        db (Session): The database session.
        budget (BudgetCreate): The budget data schema.
        user_id (int): The ID of the user creating the budget.

    Returns:
        Budgets: The created budget object.
    """
    db_budget = Budgets(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_budget_by_category(db: Session, user_id: int, category: str, month: int):
    """
    Retrieves a specific budget based on category and month.

    Useful for checking if a budget already exists to prevent duplicates.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.
        category (str): The category name.
        month (int): The month number (1-12).

    Returns:
        Budgets | None: The budget object if found, otherwise None.
    """
    return (
        db.query(Budgets)
        .filter(
            Budgets.user_id == user_id,
            Budgets.category == category,
            Budgets.month == month,
        )
        .first()
    )


def update_budget(db: Session, budget_id: int, budget_data: BudgetCreate, user_id: int):
    """
    Updates an existing budget with new data.

    Only the fields provided in `budget_data` will be updated.

    Args:
        db (Session): The database session.
        budget_id (int): The ID of the budget to update.
        budget_data (BudgetCreate): The new data schema.
        user_id (int): The ID of the user.

    Returns:
        Budgets | None: The updated budget object, or None if not found.
    """
    db_budget = (
        db.query(Budgets)
        .filter(Budgets.id == budget_id, Budgets.user_id == user_id)
        .first()
    )
    if not db_budget:
        return None

    update_data = budget_data.model_dump(exclude_unset=True)

    if "id" in update_data:
        del update_data["id"]
    if "user_id" in update_data:
        del update_data["user_id"]

    for key, value in update_data.items():
        setattr(db_budget, key, value)

    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, budget_id: int, user_id: int):
    """
    Deletes a budget record if it exists and belongs to the user.

    Args:
        db (Session): The database session.
        budget_id (int): The ID of the budget to delete.
        user_id (int): The ID of the user.

    Returns:
        Budgets | None: The deleted budget object if found, otherwise None.
    """
    budget = (
        db.query(Budgets)
        .filter(Budgets.id == budget_id, Budgets.user_id == user_id)
        .first()
    )
    if budget:
        db.delete(budget)
        db.commit()
    return budget
