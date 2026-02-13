from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=Task, status_code=201)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
):
    return task_service.create_task(db, data)


@router.get("/", response_model=list[Task])
def list_tasks(
    done: bool | None = Query(None),
    db: Session = Depends(get_db),
):
    return task_service.list_tasks(db, done)


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    return task_service.get_task(db, task_id)


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
):
    return task_service.update_task(db, task_id, data)


@router.patch("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    return task_service.complete_task(db, task_id)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    task_service.delete_task(db, task_id)
