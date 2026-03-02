"""
Test database configuration for unit tests.

This module configures an in-memory SQLite database to be used
exclusively in unit tests. Each test receives an isolated database
schema and session, ensuring full test independence and fast execution.

Key characteristics:
- Uses SQLite in-memory database
- Creates all tables before each test
- Drops all tables after each test
- Does not require Docker or external services
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base


# ======================================================
# Database configuration (SQLite in-memory)
# ======================================================

# SQLite in-memory database URL.
# The database exists only during the test execution.
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# SQLAlchemy engine for the in-memory database.
# check_same_thread=False allows multiple sessions/threads,
# which is required by SQLAlchemy and pytest internals.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

# Session factory used in tests.
# - autocommit=False: explicit commits only
# - autoflush=False: full control over when data is flushed
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ======================================================
# Pytest fixtures
# ======================================================

@pytest.fixture()
def db_session():
    """
    Provides an isolated SQLAlchemy session for unit tests.

    Lifecycle per test:
    1. Creates all database tables based on SQLAlchemy models
    2. Opens a new database session
    3. Yields the session to the test
    4. Closes the session after the test
    5. Drops all database tables

    This guarantees:
    - Full isolation between tests
    - No shared state
    - Fast execution using in-memory database
    """
    # Create all tables before the test runs
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        # Close the session and clean up schema after the test
        db.close()
        Base.metadata.drop_all(bind=engine)
