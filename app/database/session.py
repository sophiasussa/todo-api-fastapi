import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Load environment variables from the .env file.
# This allows database configuration without exposing credentials in code.
load_dotenv()

#: Database connection URL.
#: Example:
#: postgresql+psycopg2://user:password@host:5432/database
DATABASE_URL = os.getenv("DATABASE_URL")

#: SQLAlchemy engine responsible for managing database connections.
#:
#: - `pool_pre_ping=True` ensures that broken connections
#:   are detected and automatically recreated.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

#: SQLAlchemy session factory.
#:
#: Each call to `SessionLocal()` creates a new database session,
#: which must be properly closed after use — typically via
#: a FastAPI dependency.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
