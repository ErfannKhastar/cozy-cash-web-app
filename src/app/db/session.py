"""
Database Session Management.

This module sets up the SQLAlchemy engine and session factory.
It provides the `get_db` dependency used by FastAPI endpoints to obtain
a database session for each request and ensure it closes afterwards.
"""

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import declarative_base, sessionmaker
from src.app.core.config import settings


SQLALCHEMY_DATABASE_URL = URL.create(
    drivername="postgresql",
    username=settings.database_user,
    password=settings.database_password,
    host=settings.database_host,
    port=settings.database_port,
    database=settings.database_name
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
