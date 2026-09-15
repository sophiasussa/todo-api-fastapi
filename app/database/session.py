import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Load environment variables from the .env file.
# This allows database configuration without exposing credentials in code.
load_dotenv()

#: Database connection URL.
#: Example:
#: postgresql+psycopg2://user:password@host:5432/database
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite+aiosqlite:///./todo.db",
)


def async_database_url(url: str) -> str:
    """Convert a database URL to the async SQLAlchemy dialect."""
    if url.startswith("postgresql+psycopg2://"):
        return url.replace("postgresql+psycopg2://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url

#: SQLAlchemy engine responsible for managing database connections.
#:
#: - `pool_pre_ping=True` ensures that broken connections
#:   are detected and automatically recreated.
engine = create_async_engine(
    async_database_url(DATABASE_URL),
    pool_pre_ping=True,
)

#: SQLAlchemy session factory.
#:
#: Each call to `SessionLocal()` creates a new database session,
#: which must be properly closed after use — typically via
#: a FastAPI dependency.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)
