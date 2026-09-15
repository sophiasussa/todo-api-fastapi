from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import SessionLocal


async def get_db() -> AsyncIterator[AsyncSession]:
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
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
