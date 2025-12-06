"""
User Management Endpoints.

This module provides API endpoints for user-related operations, including
registering new users (sign-up) and retrieving the current user's profile information.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.app.db.session import get_db
from src.app.schemas import users as user_schemas
from src.app.crud import users as crud_users
from src.app.api import deps
from src.app.models.users import Users


router = APIRouter()


@router.post(
    "/", response_model=user_schemas.UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_in: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Registers a new user in the system.

    Checks if the email is already registered. If not, creates a new user record.

    Args:
        user_in (UserCreate): The user registration data (email, password).
        db (Session): Database session dependency.

    Returns:
        Users: The created user object.

    Raises:
        HTTPException(400): If a user with the given email already exists.
    """
    user = crud_users.get_user_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    user = crud_users.create_user(db, user=user_in)
    return user


@router.get("/me", response_model=user_schemas.UserResponse)
def read_users_me(current_user: Users = Depends(deps.get_current_user)):
    """
    Retrieves the profile of the currently authenticated user.

    This endpoint requires a valid access token.

    Args:
        current_user (Users): The user object obtained from the token dependency.

    Returns:
        Users: The detailed profile of the current user.
    """
    return current_user
