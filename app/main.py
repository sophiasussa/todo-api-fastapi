from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from app.exceptions.base import AppError
from app.routes.task import router as tasks_router

app = FastAPI(title="Todo API")

app = FastAPI()
@app.get("/")
def root():
    return {"status": "ok"}

app.include_router(tasks_router)

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
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
