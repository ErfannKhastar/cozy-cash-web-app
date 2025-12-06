"""
CRUD Interface Layer.

This module acts as a facade for the CRUD (Create, Read, Update, Delete) operations.
It aggregates and re-exports functions from individual sub-modules (users, expenses,
budgets, analytics) to provide a single, clean import point for the rest of the application.
Instead of importing from `src.app.crud.users`, other modules can import directly from `src.app.crud`.
"""

from .users import create_user, get_user_by_email, get_user_by_id
from .expenses import (
    create_expense,
    get_expenses,
    get_expense_by_id,
    delete_expense,
    update_expense,
)
from .budgets import (
    create_budget,
    get_budgets,
    get_budget_by_category,
    update_budget,
    delete_budget,
)
from .analytics import (
    get_total_spent,
    get_total_budget,
    get_top_category,
    get_category_breakdown_data,
    get_daily_spending,
)
