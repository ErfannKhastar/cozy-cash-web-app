"""
API Dependencies and Security.

This module defines reusable dependencies for FastAPI endpoints, primarily
focusing on authentication and authorization. It handles the creation of
access tokens (JWT) and the retrieval of the current authenticated user
from the database using the provided token.
"""

from typing import Optional
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from src.app.core.config import settings
from src.app.db.session import get_db
from src.app.models.users import Users
from src.app.crud import users as crud_users
from src.app.schemas import token as token_schemas


token_url = (
    f"{settings.api_v1_str}/auth/login"
    if hasattr(settings, "api_v1_str")
    else "/auth/login"
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=token_url)

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict) -> str:
    """
    Generates a JSON Web Token (JWT) for user authentication.

    Args:
        data (dict): The payload data to encode into the token (e.g., user ID).

    Returns:
        str: The encoded JWT string with an expiration time.
    """
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> Users:
    """
    Validates the access token and retrieves the current user.

    This function is used as a FastAPI dependency to protect endpoints.
    It decodes the JWT, extracts the user ID, and fetches the user from the database.

    Args:
        db (Session): The database session.
        token (str): The OAuth2 access token extracted from the request header.

    Returns:
        Users: The authenticated user object.

    Raises:
        HTTPException: If the token is invalid, expired, or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[int] = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

        token_data = token_schemas.TokenData(id=user_id)

    except JWTError:
        raise credentials_exception

    if token_data.id is None:
        raise credentials_exception

    user = crud_users.get_user_by_id(db, user_id=token_data.id)

    if user is None:
        raise credentials_exception

    return user
