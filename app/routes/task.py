from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.schemas.task import TaskResponse, TaskCreate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new task.

    This endpoint receives task data, persists it in the database,
    and returns the newly created task.

    Args:
        data (TaskCreate): Data required to create a new task.
        db (Session): Database session injected by FastAPI.

    Returns:
        TaskResponse: The created task.
    """
    return task_service.create_task(db, data)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    done: bool | None = Query(
        None,
        description="Filter tasks by completion status"
    ),
    db: Session = Depends(get_db),
):
    """
    Retrieve a list of tasks.

    Optionally filters tasks by their completion status.

    Args:
        done (bool | None): If provided, filters tasks by their `done` status.
        db (Session): Database session injected by FastAPI.

    Returns:
        list[TaskResponse]: List of tasks matching the criteria.
    """
    return task_service.list_tasks(db, done)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve a single task by its identifier.

    Args:
        task_id (int): Unique identifier of the task.
        db (Session): Database session injected by FastAPI.

    Returns:
        TaskResponse: The requested task.

    Raises:
        TaskNotFoundError: If the task does not exist.
    """
    return task_service.get_task(db, task_id)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
):
    """
    Update an existing task.

    This endpoint allows updating the task title and/or completion status.

    Args:
        task_id (int): Identifier of the task to update.
        data (TaskUpdate): Fields to be updated.
        db (Session): Database session injected by FastAPI.

    Returns:
        TaskResponse: The updated task.

    Raises:
        TaskNotFoundError: If the task does not exist.
        InvalidTaskStateError: If an invalid state transition is attempted.
    """
    return task_service.update_task(db, task_id, data)


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """
    Mark a task as completed.

    Args:
        task_id (int): Identifier of the task to complete.
        db (Session): Database session injected by FastAPI.

    Returns:
        TaskResponse: The completed task.

    Raises:
        TaskNotFoundError: If the task does not exist.
        TaskAlreadyCompletedError: If the task is already completed.
    """
    return task_service.complete_task(db, task_id)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
):
    """
    Delete a task by its identifier.

    Args:
        task_id (int): Identifier of the task to delete.
        db (Session): Database session injected by FastAPI.

    Raises:
        TaskNotFoundError: If the task does not exist.
    """
    task_service.delete_task(db, task_id)
