"""
User API Tests.

This module contains tests for user authentication and management.
It covers scenarios such as:
- User registration (successful and duplicate handling).
- Authentication logic (login success, incorrect credentials).
- Token validation and retrieving the current user's profile.
"""
import pytest
from jose import jwt
from src.app.schemas import users
from src.app.schemas import token
from src.app.core.config import settings


def test_create_user(client):
    """
    Test that a new user can be successfully registered via the API.
    Verifies the response status code, email accuracy, and ID assignment.
    """
    response = client.post(
        "/api/v1/users",
        json={"email": "asd@gmail.com", "password": "asd123"},
    )

    new_user = users.UserResponse(**response.json())

    assert response.status_code == 201
    assert new_user.email == "asd@gmail.com"
    assert new_user.id is not None


def test_create_user_already_exists(client, test_user):
    """
    Test that registering a user with an email that already exists fails.
    Verifies the 400 status code and the specific error detail message.
    """
    response = client.post(
        "/api/v1/users",
        json={"email": test_user["email"], "password": test_user["password"]},
    )

    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The user with this email already exists in the system."
    )


def test_login_success(client, test_user):
    """
    Test that a registered user can successfully log in and receive an access token.
    Verifies the 200 status code and the token structure (access_token, token_type).
    """
    login_data = {"username": test_user["email"], "password": test_user["password"]}

    response = client.post(
        "/api/v1/auth/login",
        data=login_data,
    )

    token_data = token.Token(**response.json())

    payload = jwt.decode(
        token_data.access_token,
        settings.secret_key,
        algorithms=settings.algorithm,
    )

    id = payload["user_id"]

    assert response.status_code == 200
    assert id == test_user["id"]
    assert token_data.token_type == "bearer"
    assert token_data.access_token is not None


def test_login_wrong_password(client, test_user):
    """
    Test that logging in with an incorrect password fails.
    Verifies the 401 status code and the error message.
    """
    login_data = {
        "username": test_user["email"],
        "password": "wrongpassword123",
    }

    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_non_existent_user(client):
    """
    Test that logging in with a non-registered email address fails.
    Verifies the 401 status code.
    """
    login_data = {
        "username": "ghost@example.com",
        "password": "somepassword",
    }

    response = client.post("/api/v1/auth/login", data=login_data)

    assert response.status_code == 401


def test_read_users_me(authorized_client, test_user):
    """
    Test retrieving the currently authenticated user's profile.
    Requires a valid access token. Verifies the 200 status code and data matching.
    """
    response = authorized_client.get("/api/v1/users/me")

    assert response.status_code == 200
    assert response.json()["email"] == test_user["email"]
    assert response.json()["id"] == test_user["id"]


def test_unauthorized_read_users_me(client):
    """
    Test that accessing the user profile endpoint without authentication fails.
    Verifies the 401 status code.
    """
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
