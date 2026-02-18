from sqlalchemy.orm import Session
from app.database.session import SessionLocal


def get_db() -> Session:
    """
    FastAPI dependency responsible for providing a database session.

    This function creates a new SQLAlchemy session for each request
    and ensures that it is properly closed at the end of the request
    lifecycle, even in case of errors.

    It should be used with `Depends(get_db)` in routes or services
    that require access to the database.

    Yields:
        Session: an active SQLAlchemy session bound to the current request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
