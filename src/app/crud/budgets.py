from typing import List
from sqlalchemy.orm import Session
from src.app.models.budgets import Budgets
from src.app.schemas.budgets import BudgetCreate


def get_budgets(
    db: Session, user_id: int, skip: int = 0, limit: int = 100
) -> List[Budgets]:
    return (
        db.query(Budgets)
        .filter(Budgets.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_budget(db: Session, budget: BudgetCreate, user_id: int):
    db_budget = Budgets(**budget.model_dump(), user_id=user_id)
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def get_budget_by_category(db: Session, user_id: int, category: str, month):
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
    db_budget = (
        db.query(Budgets)
        .filter(Budgets.id == budget_id, Budgets.user_id == user_id)
        .first()
    )
    if not db_budget:
        return None

    update_data = budget_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_budget, key, value)

    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


def delete_budget(db: Session, budget_id: int, user_id: int):
    budget = (
        db.query(Budgets)
        .filter(Budgets.id == budget_id, Budgets.user_id == user_id)
        .first()
    )
    if budget:
        db.delete(budget)
        db.commit()
    return budget
