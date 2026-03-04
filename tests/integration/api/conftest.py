"""
Integration and concurrency test configuration.

This module configures the test environment for tests that:

- Run against a real database (defined by TEST_DATABASE_URL)
- Apply real Alembic migrations
- Use FastAPI TestClient
- Test full request → service → database flow

Unlike unit tests:
- This setup does NOT use SQLite in-memory
- It requires a running database (e.g., Docker/Postgres)
- It validates the real database schema via migrations

All integration and concurrency tests depend on this configuration.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from alembic import command
from alembic.config import Config

from app.main import app
from app.database.dependencies import get_db


# ======================================================
# Alembic – apply migrations to TEST database
# ======================================================

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    Apply all Alembic migrations to the test database before
    any test is executed.

    Behavior:
    - Reads TEST_DATABASE_URL from environment
    - Configures Alembic programmatically
    - Executes `upgrade head`

    This ensures:
    - The database schema matches production schema
    - Tests run against the real migrated structure
    """
    db_url = os.getenv("TEST_DATABASE_URL")
    if not db_url:
        raise RuntimeError("TEST_DATABASE_URL not set")

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../")
    )

    alembic_ini_path = os.path.join(PROJECT_ROOT, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)

    # Ensure Alembic finds the migration scripts directory
    alembic_cfg.set_main_option(
        "script_location",
        os.path.join(PROJECT_ROOT, "alembic"),
    )

    # Force the test database URL
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    # Apply all migrations up to the latest revision
    command.upgrade(alembic_cfg, "head")


# ======================================================
# Database session (per test)
# ======================================================

# Engine connected to the real test database
engine = create_engine(
    os.environ["TEST_DATABASE_URL"],
    pool_pre_ping=True,  # Ensures stale connections are refreshed
)

# Session factory for integration tests
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture(scope="function")
def db_session():
    """
    Provides a database session for each test function.

    This fixture:
    - Opens a new session
    - Yields it to the test
    - Closes it after test completion

    It does NOT recreate tables (migrations already applied at session start).
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_db():
    """
    Cleans database state before each test.

    Uses TRUNCATE with RESTART IDENTITY and CASCADE to:
    - Remove all rows from the tasks table
    - Reset auto-increment IDs
    - Remove dependent records if necessary

    This guarantees test isolation without re-running migrations.
    """
    db = TestingSessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE"))
        db.commit()
    finally:
        db.close()


# ======================================================
# FastAPI TestClient with dependency override
# ======================================================

@pytest.fixture(scope="function")
def client():
    """
    Provides a FastAPI TestClient configured to use the
    test database session instead of the production dependency.

    Behavior:
    - Overrides `get_db` dependency
    - Injects TestingSessionLocal
    - Clears overrides after test

    This ensures:
    - Full request lifecycle testing
    - Real database interaction
    - Isolation from production configuration
    """
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Override the application's database dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    # Remove dependency overrides after test
    app.dependency_overrides.clear()
