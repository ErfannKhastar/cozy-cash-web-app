from typing import List
from sqlalchemy.orm import Session
from src.app.models.expenses import Expenses
from src.app.schemas.expenses import ExpenseCreate


def get_expenses(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Expenses]:
    return (
        db.query(Expenses)
        .filter(Expenses.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_expense(db: Session, expense: ExpenseCreate, user_id: int):
    db_expense = Expenses(**expense.model_dump(), user_id=user_id)
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense


def get_expense_by_id(db: Session, expense_id: int, user_id: int):
    return (
        db.query(Expenses)
        .filter(Expenses.id == expense_id, Expenses.user_id == user_id)
        .first()
    )


def delete_expense(db: Session, expense_id: int, user_id: int):
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
    db_expense = (
        db.query(Expenses)
        .filter(Expenses.id == expense_id, Expenses.user_id == user_id)
        .first()
    )
    if not db_expense:
        return None

    update_data = expense_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_expense, key, value)

    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense
