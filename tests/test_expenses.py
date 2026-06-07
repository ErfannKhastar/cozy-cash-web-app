"""
Expense API Tests.

This module tests the CRUD operations for user expenses.
It verifies:
- Creating expenses (with manual and default dates).
- Retrieving expenses (listing and pagination).
- Updating and deleting existing expenses.
- Security checks (unauthorized access, modifying other users' data).
- Error handling (not found items).
"""
import pytest
from datetime import datetime
from jose import jwt
from src.app.schemas import expenses
from src.app.schemas import token
from src.app.schemas import users
from src.app.core import config


def test_get_all_expenses(authorized_client, sample_expenses):
    """
    Test retrieving a list of expenses for the authenticated user.
    Verifies the 200 OK status and the correct count of returned items.
    """
    response = authorized_client.get("/api/v1/expenses")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_unauthorized_get_all_expenses(client):
    """
    Test that unauthenticated users cannot access the expenses list.
    Verifies the 401 Unauthorized status.
    """
    response = client.get("/api/v1/expenses")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_pagination(authorized_client, sample_expenses):
    """
    Test the pagination functionality (skip and limit).
    Verifies that the API correctly slices the result set based on query params.
    """
    response = authorized_client.get("/api/v1/expenses?limit=1&skip=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    # Verifies that the returned item is indeed the second one (skip=1)
    assert response.json()[0]["id"] == sample_expenses[1].id


@pytest.mark.parametrize(
    "amount, description, category, date",
    [
        (10, "pizza", "food", None),
        (20, "cheese", "food", "2025-01-01T12:00:00"),
        (30, "breakfast", "food", None),
    ],
)
def test_create_expense(authorized_client, amount, description, category, date):
    """
    Test creating a new expense with various data combinations.

    Uses parametrization to test:
    1. Creating an expense without a date (DB should set default).
    2. Creating an expense with a specific provided date.
    """
    payload = {
        "amount": amount,
        "description": description,
        "category": category,
    }

    if date is not None:
        payload["date"] = date

    response = authorized_client.post(
        "/api/v1/expenses",
        json=payload,
    )

    created_expense = expenses.ExpenseResponse(**response.json())

    assert response.status_code == 201
    assert created_expense.amount == amount
    assert created_expense.description == description
    assert created_expense.category == category

    if date:
        # If date was provided, verified it matches the input
        assert str(created_expense.date).startswith(date.split("T")[0])
    else:
        # If no date provided, verify DB assigned a default value (not None)
        assert created_expense.date is not None


def test_unauthorized_create_expense(client):
    """
    Test that unauthenticated users cannot create expenses.
    Verifies the 401 Unauthorized status.
    """
    payload = {
        "amount": 10,
        "description": "pizza",
        "category": "cheese",
        "date": "2025-01-01T12:00:00",
    }

    response = client.post(
        "/api/v1/expenses",
        json=payload,
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_expense(authorized_client, sample_expenses):
    """
    Test updating an existing expense belonging to the user.
    Verifies the 200 OK status and that fields are correctly updated.
    """
    payload = {
        "amount": 10,
        "description": "pizza",
        "category": "cheese",
    }

    response = authorized_client.put(
        f"/api/v1/expenses/{sample_expenses[0].id}",
        json=payload,
    )

    updated_expense = expenses.ExpenseResponse(**response.json())

    assert response.status_code == 200
    assert updated_expense.amount == 10
    assert updated_expense.description == "pizza"
    assert updated_expense.category == "cheese"
    assert updated_expense.id == sample_expenses[0].id
    assert updated_expense.date is not None


def test_unauthorized_update_expense(client, sample_expenses):
    """
    Test that unauthenticated users cannot update expenses.
    Verifies the 401 Unauthorized status.
    """
    payload = {
        "amount": 10,
        "description": "pizza",
        "category": "cheese",
    }

    response = client.put(
        f"/api/v1/expenses/{sample_expenses[0].id}",
        json=payload,
    )

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_other_user_expense(authorized_client, sample_expenses):
    """
    Test security isolation: A user cannot update another user's expense.

    Attempts to update the last expense (belonging to User 2) with User 1's token.
    Should return 404 Not Found (or 403 Forbidden).
    """
    payload = {
        "amount": 10,
        "description": "pizza",
        "category": "cheese",
        "date": "2025-01-01T12:00:00",
    }

    response = authorized_client.put(
        f"/api/v1/expenses/{sample_expenses[-1].id}",
        json=payload,
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}


def test_update_non_existent_expense(authorized_client):
    """
    Test updating an expense ID that does not exist in the database.
    Verifies the 404 Not Found status.
    """
    payload = {"amount": 20, "description": "pizza", "category": "food"}

    response = authorized_client.put("/api/v1/expenses/99999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}


def test_delete_expense(authorized_client, sample_expenses):
    """
    Test deleting an existing expense belonging to the user.
    Verifies the 204 No Content status.
    """
    response = authorized_client.delete(f"/api/v1/expenses/{sample_expenses[0].id}")

    assert response.status_code == 204


def test_unauthorized_delete_expense(client, sample_expenses):
    """
    Test that unauthenticated users cannot delete expenses.
    Verifies the 401 Unauthorized status.
    """
    response = client.delete(f"/api/v1/expenses/{sample_expenses[0].id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_other_user_expense(authorized_client, sample_expenses):
    """
    Test security isolation: A user cannot delete another user's expense.
    Verifies the 404 Not Found status when accessing User 2's data.
    """
    other_user_expense = sample_expenses[-1]

    response = authorized_client.delete(f"/api/v1/expenses/{other_user_expense.id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}


def test_delete_non_existent_expense(authorized_client):
    """
    Test deleting an expense ID that does not exist.
    Verifies the 404 Not Found status.
    """
    response = authorized_client.delete("/api/v1/expenses/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Expense not found"}
