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
# Alembic – migrations no banco de TESTE
# ======================================================

@pytest.fixture(scope="session", autouse=True)
def apply_migrations():
    """
    Aplica migrations no banco de teste antes de qualquer teste rodar.
    """
    db_url = os.getenv("TEST_DATABASE_URL")
    if not db_url:
        raise RuntimeError("TEST_DATABASE_URL not set")

    PROJECT_ROOT = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../")
    )

    alembic_ini_path = os.path.join(PROJECT_ROOT, "alembic.ini")
    alembic_cfg = Config(alembic_ini_path)

    # garante que o Alembic encontre a pasta "alembic/"
    alembic_cfg.set_main_option(
        "script_location",
        os.path.join(PROJECT_ROOT, "alembic"),
    )

    # força o banco de TESTE
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)

    command.upgrade(alembic_cfg, "head")


# ======================================================
# Database session (por teste)
# ======================================================

engine = create_engine(
    os.environ["TEST_DATABASE_URL"],
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

@pytest.fixture(scope="function")
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def clean_db(db_session):
    db_session.execute(
        text("TRUNCATE TABLE tasks RESTART IDENTITY CASCADE")
    )
    db_session.commit()
    yield

# ======================================================
# FastAPI TestClient com override de dependência
# ======================================================

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
