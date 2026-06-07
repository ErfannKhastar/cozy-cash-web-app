"""
Pytest Configuration and Fixtures.

This module defines shared fixtures for the test suite, handling:
- Database connection and transaction management.
- Alembic migrations for setting up the test schema.
- Test client creation for FastAPI.
- seeding the database with initial test data (users, expenses, budgets).
"""
import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from alembic.config import Config as AlembicConfig
from alembic import command
from src.app.main import app
from src.app.core.config import settings
from src.app.db.session import get_db
from src.app.api.deps import create_access_token
from src.app.core.security import hash_password
from src.app.models import users as user_models
from src.app.models import expenses as expense_models
from src.app.models import budgets as budget_models
from datetime import datetime, date


# Connection URL for the dedicated test database
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session")
def apply_migrations():
    """
    Applies database migrations at the start of the test session.

    It runs Alembic 'upgrade head' to create tables and 'downgrade base'
    after the session ends to clean up.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini_path = os.path.join(base_dir, "alembic.ini")

    alembic_cfg = AlembicConfig(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "alembic"))

    # Flag to prevent env.py from overriding the test database URL
    alembic_cfg.attributes["is_test_run"] = True

    try:
        command.downgrade(alembic_cfg, "base")
    except:
        pass

    command.upgrade(alembic_cfg, "head")

    yield

    command.downgrade(alembic_cfg, "base")


@pytest.fixture(scope="function")
def db_session(apply_migrations):
    """
    Creates a fresh database session for each test function.

    Wraps the test in a transaction and rolls it back after execution,
    ensuring isolation between tests.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    Creates a FastAPI TestClient with a database dependency override.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session):
    """
    Creates a sample user (User 1) in the database.
    """
    user_data = {"email": "user1@example.com", "password": "password123"}
    hashed = hash_password(user_data["password"])
    new_user = user_models.Users(email=user_data["email"], password=hashed)

    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "password": user_data["password"],
        "obj": new_user,
    }


@pytest.fixture
def test_user2(db_session):
    """
    Creates a second sample user (User 2) for testing permissions and isolation.
    """
    user_data = {"email": "user2@example.com", "password": "password123"}
    hashed = hash_password(user_data["password"])
    new_user = user_models.Users(email=user_data["email"], password=hashed)

    db_session.add(new_user)
    db_session.commit()
    db_session.refresh(new_user)

    return {
        "id": new_user.id,
        "email": new_user.email,
        "password": user_data["password"],
        "obj": new_user,
    }


@pytest.fixture
def token(test_user):
    """
    Generates a valid JWT access token for User 1.
    """
    return create_access_token({"user_id": test_user["id"]})


@pytest.fixture
def authorized_client(client, token):
    """
    Returns a TestClient authenticated as User 1.
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}
    return client


@pytest.fixture
def sample_expenses(db_session, test_user, test_user2):
    """
    Seeds the database with sample expense records for both users.
    """
    expenses_data = [
        {
            "amount": 100,
            "description": "Lunch",
            "category": "Food",
            "user_id": test_user["id"],
            "date": datetime.now(),
        },
        {
            "amount": 50,
            "description": "Taxi",
            "category": "Transport",
            "user_id": test_user["id"],
            "date": datetime.now(),
        },
        {
            "amount": 2000,
            "description": "Rent",
            "category": "Housing",
            "user_id": test_user["id"],
            "date": datetime.now(),
        },
        {
            "amount": 500,
            "description": "Secret Gift",
            "category": "Gifts",
            "user_id": test_user2["id"],
            "date": datetime.now(),
        },
    ]

    expense_objects = [expense_models.Expenses(**data) for data in expenses_data]

    db_session.add_all(expense_objects)
    db_session.commit()

    return db_session.query(expense_models.Expenses).all()


@pytest.fixture
def sample_budgets(db_session, test_user, test_user2):
    """
    Seeds the database with sample budget records for both users.
    """
    budgets_data = [
        {
            "amount": 100,
            "category": "Food",
            "month": date(2025, 1, 1),
            "user_id": test_user["id"],
        },
        {
            "amount": 50,
            "category": "Transport",
            "month": date(2025, 2, 1),
            "user_id": test_user["id"],
        },
        {
            "amount": 200,
            "category": "Housing",
            "month": date(2025, 3, 1),
            "user_id": test_user["id"],
        },
        {
            "amount": 500,
            "category": "Gifts",
            "month": date(2025, 4, 1),
            "user_id": test_user2["id"],
        },
    ]

    budget_objects = [budget_models.Budgets(**data) for data in budgets_data]

    db_session.add_all(budget_objects)
    db_session.commit()

    return db_session.query(budget_models.Budgets).all()
