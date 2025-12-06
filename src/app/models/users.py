"""
User Database Model.

Represents the 'users' table in the database, storing authentication credentials
and account metadata.
"""

from sqlalchemy import Column, String, Integer, TIMESTAMP, text
from src.app.db.session import Base


class Users(Base):
    """
    SQLAlchemy model for Users.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
