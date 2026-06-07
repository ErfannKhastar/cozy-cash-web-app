"""
Budget API Tests.

This module tests the CRUD operations for user budgets.
It verifies:
- Creating budgets (ensuring valid dates and unique category/month constraints).
- Retrieving budgets (listing and pagination).
- Updating and deleting existing budgets.
- Security checks (unauthorized access, modifying other users' data).
- Validation errors (invalid date formats, duplicate entries).
"""
import pytest
from datetime import datetime, date
from jose import jwt
from src.app.schemas import users
from src.app.schemas import expenses
from src.app.schemas import budgets
from src.app.schemas import token
from src.app.core import config


def test_get_all_budgets(authorized_client, sample_budgets):
    """
    Test retrieving a list of budgets for the authenticated user.
    Verifies the 200 OK status and the correct count of returned items.
    """
    response = authorized_client.get("/api/v1/budgets")

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_unauthorized_get_all_budgets(client):
    """
    Test that unauthenticated users cannot access the budget list.
    Verifies the 401 Unauthorized status.
    """
    response = client.get("/api/v1/budgets")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_pagination(authorized_client, sample_budgets):
    """
    Test the pagination functionality (skip and limit).
    Verifies that the API correctly slices the result set based on query params.
    """
    response = authorized_client.get("/api/v1/budgets?limit=1&skip=1")

    assert response.status_code == 200
    assert len(response.json()) == 1
    # Verifies that the returned item is indeed the second one (skip=1)
    assert response.json()[0]["id"] == sample_budgets[1].id


@pytest.mark.parametrize(
    "amount, category, month",
    [
        (500, "food", "2025-02-01"),
        (50, "taxi", "2025-03-01"),
        (250, "game", "2025-04-01"),
    ],
)
def test_create_budget(authorized_client, amount, category, month):
    """
    Test creating a new budget with valid data.
    Uses parametrization to test different amounts and months.
    """
    payload = {"amount": amount, "category": category, "month": month}

    response = authorized_client.post("/api/v1/budgets", json=payload)

    created_budget = budgets.BudgetResponse(**response.json())

    assert response.status_code == 201
    assert created_budget.amount == amount
    assert created_budget.category == category
    # Ensure the returned date object matches the input string
    assert str(created_budget.month) == month


def test_unauthorized_create_budget(client):
    """
    Test that unauthenticated users cannot create budgets.
    Verifies the 401 Unauthorized status.
    """
    payload = {"amount": 10, "category": "food", "month": "2025-02-01"}

    response = client.post("/api/v1/budgets", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_create_duplicate_budget(authorized_client, sample_budgets):
    """
    Test the unique constraint logic.
    A user cannot create two budgets for the same category in the same month.
    Expects a 400 Bad Request (or 409 Conflict) error.
    """
    # Pick an existing budget from the fixture to try and duplicate
    existing_budget = sample_budgets[0]

    payload = {
        "amount": 900,
        "category": existing_budget.category,
        "month": str(existing_budget.month),
    }

    response = authorized_client.post("/api/v1/budgets", json=payload)

    assert response.status_code == 400
    assert response.json() == {"detail": "Budget for this category and month already exists"}


def test_create_budget_invalid_data(authorized_client):
    """
    Test data validation checks.
    Sending an invalid date string should trigger a 422 Unprocessable Entity error.
    """
    payload = {"amount": -50, "category": "Food", "month": "invalid-date"}

    response = authorized_client.post("/api/v1/budgets", json=payload)

    assert response.status_code == 422


def test_update_budget(authorized_client, sample_budgets):
    """
    Test updating an existing budget belonging to the user.
    Verifies that fields like amount can be modified.
    """
    payload = {"amount": 10, "category": "food", "month": "2025-02-01"}

    response = authorized_client.put(
        f"/api/v1/budgets/{sample_budgets[0].id}", json=payload
    )

    updated_budget = budgets.BudgetResponse(**response.json())

    assert response.status_code == 200
    assert updated_budget.amount == 10
    assert updated_budget.category == "food"
    assert str(updated_budget.month) == "2025-02-01"


def test_unauthorized_update_budget(client, sample_budgets):
    """
    Test that unauthenticated users cannot update budgets.
    Verifies the 401 Unauthorized status.
    """
    payload = {"amount": 10, "category": "food", "month": "2025-02-01"}

    response = client.put(f"/api/v1/budgets/{sample_budgets[0].id}", json=payload)

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_update_other_user_budget(authorized_client, sample_budgets):
    """
    Test security isolation: A user cannot update another user's budget.
    The last item in sample_budgets belongs to User 2.
    """
    payload = {
        "amount": 10,
        "category": "food",
        "month": "2025-02-01",
    }

    response = authorized_client.put(
        f"/api/v1/budgets/{sample_budgets[-1].id}", json=payload
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget not found"}


def test_update_non_existent_budget(authorized_client):
    """
    Test updating a budget ID that does not exist.
    Verifies the 404 Not Found status.
    """
    payload = {"amount": 0, "category": "food", "month": "2025-02-01"}

    response = authorized_client.put(f"/api/v1/budgets/99999", json=payload)

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget not found"}


def test_delete_budget(authorized_client, sample_budgets):
    """
    Test deleting an existing budget belonging to the user.
    Verifies the 204 No Content status.
    """
    response = authorized_client.delete(f"/api/v1/budgets/{sample_budgets[0].id}")

    assert response.status_code == 204


def test_unauthorized_delete_budget(client, sample_budgets):
    """
    Test that unauthenticated users cannot delete budgets.
    Verifies the 401 Unauthorized status.
    """
    response = client.delete(f"/api/v1/budgets/{sample_budgets[0].id}")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


def test_delete_other_user_budget(authorized_client, sample_budgets):
    """
    Test security isolation: A user cannot delete another user's budget.
    Verifies the 404 Not Found status.
    """
    response = authorized_client.delete(f"/api/v1/budgets/{sample_budgets[-1].id}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget not found"}


def test_delete_non_existent_budget(authorized_client):
    """
    Test deleting a budget ID that does not exist.
    Verifies the 404 Not Found status.
    """
    response = authorized_client.delete(f"/api/v1/budgets/99999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Budget not found"}
