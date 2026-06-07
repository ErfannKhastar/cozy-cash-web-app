"""
Authentication Endpoints.

This module handles user authentication operations, specifically the login process
and the generation of JSON Web Tokens (JWT) for session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from src.app.core import security
from src.app.db.session import get_db
from src.app.crud import users as crud_users
from src.app.api import deps
from src.app.schemas import token as token_schemas


router = APIRouter()


@router.post("/login", response_model=token_schemas.Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """
    Authenticates a user and returns an access token.

    This endpoint takes a username (email) and password via OAuth2 form data,
    verifies the credentials against the database, and creates a JWT access token
    if valid.

    Args:
        db (Session): Database session dependency.
        form_data (OAuth2PasswordRequestForm): Form containing username and password.

    Returns:
        dict: A dictionary containing the access token and token type (bearer).

    Raises:
        HTTPException(401): If email is not found or password is incorrect.
    """
    user = crud_users.get_user_by_email(db, email=form_data.username)

    if not user or not security.verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = deps.create_access_token(data={"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
