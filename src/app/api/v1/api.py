"""
API Router Configuration (Version 1).

This module aggregates all the sub-routers (auth, users, expenses, budgets, analytics)
into a single main router for version 1 of the API. This allows `main.py` to include
all V1 endpoints with a single line of code.
"""

from fastapi import APIRouter
from src.app.api.v1.endpoints import auth, users, expenses, budgets, analytics


api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(expenses.router, prefix="/expenses", tags=["Expenses"])
api_router.include_router(budgets.router, prefix="/budgets", tags=["Budgets"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
