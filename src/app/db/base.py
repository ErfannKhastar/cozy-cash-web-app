"""
SQLAlchemy Model Registry.

This module imports all the database models (Users, Expenses, Budgets) and the Base class.
Its primary purpose is to be imported by Alembic's `env.py` so that migrations can
detect all the models and their relationships automatically.
"""

from src.app.db.session import Base
from src.app.models.users import Users
from src.app.models.expenses import Expenses
from src.app.models.budgets import Budgets
