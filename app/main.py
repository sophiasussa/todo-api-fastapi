"""
Application entrypoint.

This module is responsible for:
- Creating the FastAPI application
- Registering API routes
- Registering global exception handlers
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.exceptions.base import AppError
from app.routes.task import router as tasks_router


app = FastAPI(title="Todo API")


@app.get("/")
def root():
    """
    Health check endpoint.

    Returns:
        dict: Simple status response indicating the API is running.
    """
    return {"status": "ok"}


# Register application routers
app.include_router(tasks_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    """
    Global handler for application-specific errors.

    Converts AppError exceptions into RFC 7807 compliant JSON responses.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": exc.type,
            "title": exc.title,
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": request.url.path,
            "error_code": exc.error_code,
        },
    )
