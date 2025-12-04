from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract, cast, Date
from typing import Optional
from src.app.models.expenses import Expenses
from src.app.models.budgets import Budgets


def get_total_spent(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    query = db.query(func.sum(Expenses.amount)).filter(Expenses.user_id == user_id)
    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)
    return query.scalar() or 0


def get_total_budget(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    query = db.query(func.sum(Budgets.amount)).filter(Budgets.user_id == user_id)
    if month:
        query = query.filter(extract("month", Budgets.month) == month)
    if year:
        query = query.filter(extract("year", Budgets.month) == year)
    return query.scalar() or 0


def get_top_category(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    query = db.query(
        Expenses.category,
        func.sum(Expenses.amount).label("total"),
    ).filter(Expenses.user_id == user_id)

    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)

    result = query.group_by(Expenses.category).order_by(desc("total")).first()
    return result[0] if result else "No Data"


def get_category_breakdown_data(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    query = db.query(
        Expenses.category,
        func.sum(Expenses.amount).label("total"),
    ).filter(Expenses.user_id == user_id)

    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)

    return query.group_by(Expenses.category).all()


def get_daily_spending(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    date_only = cast(Expenses.date, Date)
    query = db.query(
        date_only.label("day"), func.sum(Expenses.amount).label("total")
    ).filter(Expenses.user_id == user_id)

    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)

    return query.group_by(date_only).order_by(date_only).all()
