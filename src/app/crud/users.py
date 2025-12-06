"""
CRUD Operations for Users.

This module contains functions to interact with the database for
User-related operations such as retrieving user details by ID or email
and creating new user records.
"""

from sqlalchemy.orm import Session
from src.app.models.users import Users
from src.app.schemas.users import UserCreate
from src.app.core.security import hash_password


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a user by their email address.

    Args:
        db (Session): The database session.
        email (str): The email address to search for.

    Returns:
        Users | None: The user object if found, otherwise None.
    """
    return db.query(Users).filter(Users.email == email).first()


def get_user_by_id(db: Session, user_id: int):
    """
    Retrieves a user by their unique ID.

    Args:
        db (Session): The database session.
        user_id (int): The ID of the user.

    Returns:
        Users | None: The user object if found, otherwise None.
    """
    return db.query(Users).filter(Users.id == user_id).first()


def create_user(db: Session, user: UserCreate):
    """
    Creates a new user in the database with a hashed password.

    Args:
        db (Session): The database session.
        user (UserCreate): The user data schema containing email and password.

    Returns:
        Users: The created user object.
    """
    hashed_pwd = hash_password(user.password)
    db_user = Users(email=user.email, password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
