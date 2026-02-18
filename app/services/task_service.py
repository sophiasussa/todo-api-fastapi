from sqlalchemy.orm import Session

from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.exceptions.task import (
    InvalidTaskStateError,
    TaskNotFoundError,
    TaskAlreadyCompletedError,
)


def get_task(db: Session, task_id: int) -> TaskModel:
    """
    Retrieve a task by its identifier.

    Args:
        db (Session): Active SQLAlchemy database session.
        task_id (int): Identifier of the task to be retrieved.

    Raises:
        TaskNotFoundError: If no task with the given ID exists.

    Returns:
        TaskModel: The task ORM model.
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    if not task:
        raise TaskNotFoundError(task_id)

    return task


def create_task(db: Session, data: TaskCreate) -> TaskModel:
    """
    Create a new task.

    Args:
        db (Session): Active SQLAlchemy database session.
        data (TaskCreate): Data required to create the task.

    Returns:
        TaskModel: The newly created task ORM model.
    """
    task = TaskModel(
        title=data.title,
        done=False,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def list_tasks(db: Session, done: bool | None = None) -> list[TaskModel]:
    """
    List tasks, optionally filtered by completion status.

    Args:
        db (Session): Active SQLAlchemy database session.
        done (bool | None): Optional filter to return only
            completed or uncompleted tasks.

    Returns:
        list[TaskModel]: List of task ORM models.
    """
    query = db.query(TaskModel)

    if done is not None:
        query = query.filter(TaskModel.done == done)

    return query.all()


def complete_task(db: Session, task_id: int) -> TaskModel:
    """
    Mark a task as completed.

    Args:
        db (Session): Active SQLAlchemy database session.
        task_id (int): Identifier of the task to be completed.

    Raises:
        TaskNotFoundError: If the task does not exist (raised by get_task).
        TaskAlreadyCompletedError: If the task is already completed.

    Returns:
        TaskModel: The updated task ORM model.
    """
    task = get_task(db, task_id)

    if task.done:
        raise TaskAlreadyCompletedError()

    task.done = True
    db.commit()
    db.refresh(task)

    return task


def update_task(
    db: Session,
    task_id: int,
    data: TaskUpdate,
) -> TaskModel:
    """
    Update an existing task.

    Supports partial updates. Business rules are enforced
    to prevent invalid state transitions.

    Args:
        db (Session): Active SQLAlchemy database session.
        task_id (int): Identifier of the task to be updated.
        data (TaskUpdate): Fields to be updated.

    Raises:
        TaskNotFoundError: If the task does not exist (raised by get_task).
        InvalidTaskStateError: If an invalid state transition
            is attempted.

    Returns:
        TaskModel: The updated task ORM model.
    """
    task = get_task(db, task_id)

    if task.done and data.done is False:
        raise InvalidTaskStateError(
            reason="Completed tasks cannot be reopened"
        )

    if data.title is not None:
        task.title = data.title

    if data.done is not None:
        task.done = data.done

    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int) -> None:
    """
    Delete a task.

    Args:
        db (Session): Active SQLAlchemy database session.
        task_id (int): Identifier of the task to be deleted.

    Raises:
        TaskNotFoundError: If the task does not exist (raised by get_task).
    """
    task = get_task(db, task_id)

    db.delete(task)
    db.commit()


def to_domain(model: TaskModel) -> TaskResponse:
    """
    Convert a Task ORM model into a response schema.

    This function isolates the mapping between persistence
    models and API response models.

    Args:
        model (TaskModel): Task ORM model.

    Returns:
        TaskResponse: Serialized task representation.
    """
    return TaskResponse(
        id=model.id,
        title=model.title,
        done=model.done,
    )
