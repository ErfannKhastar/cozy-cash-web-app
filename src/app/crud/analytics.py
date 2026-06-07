"""
Analytics and Statistics Operations.

This module performs complex database queries to calculate financial summaries,
such as total spending, remaining budgets, category breakdowns, and daily spending trends.
It uses SQLAlchemy aggregation functions (SUM, COUNT, etc.).
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, desc, extract, cast, Date
from typing import Optional
from src.app.models.expenses import Expenses
from src.app.models.budgets import Budgets


def get_total_spent(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    """
    Calculates the total amount of money spent by the user.

    Args:
        db (Session): The database session.
        user_id (int): The user's ID.
        month (int, optional): Filter by month number (1-12).
        year (int, optional): Filter by year (e.g., 2023).

    Returns:
        float: The sum of expenses, or 0 if no expenses found.
    """
    query = db.query(func.sum(Expenses.amount)).filter(Expenses.user_id == user_id)
    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)
    return query.scalar() or 0


def get_total_budget(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    """
    Calculates the total budget allocated by the user.

    Args:
        db (Session): The database session.
        user_id (int): The user's ID.
        month (int, optional): Filter by month number.
        year (int, optional): Filter by year.

    Returns:
        float: The sum of budgets, or 0 if no budgets found.
    """
    query = db.query(func.sum(Budgets.amount)).filter(Budgets.user_id == user_id)
    if month:
        query = query.filter(extract("month", Budgets.month) == month)
    if year:
        query = query.filter(extract("year", Budgets.month) == year)
    return query.scalar() or 0


def get_top_category(
    db: Session, user_id: int, month: Optional[int], year: Optional[int]
):
    """
    Identifies the category with the highest total spending.

    Args:
        db (Session): The database session.
        user_id (int): The user's ID.
        month (int, optional): Filter by month number.
        year (int, optional): Filter by year.

    Returns:
        str: The name of the category with the highest spending, or "No Data".
    """
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
    """
    Retrieves spending data grouped by category for charts.

    Args:
        db (Session): The database session.
        user_id (int): The user's ID.
        month (int, optional): Filter by month number.
        year (int, optional): Filter by year.

    Returns:
        list: A list of tuples/objects containing category names and total amounts.
    """
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
    """
    Retrieves total spending grouped by day for trend charts.

    Args:
        db (Session): The database session.
        user_id (int): The user's ID.
        month (int, optional): Filter by month number.
        year (int, optional): Filter by year.

    Returns:
        list: A list of results containing the date and total amount for that day.
    """
    date_only = cast(Expenses.date, Date)
    query = db.query(
        date_only.label("day"), func.sum(Expenses.amount).label("total")
    ).filter(Expenses.user_id == user_id)

    if month:
        query = query.filter(extract("month", Expenses.date) == month)
    if year:
        query = query.filter(extract("year", Expenses.date) == year)

    return query.group_by(date_only).order_by(date_only).all()
