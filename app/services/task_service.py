from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse
from app.exceptions.task import (
    InvalidTaskStateError,
    TaskNotFoundError,
    TaskAlreadyCompletedError,
)


async def get_task(db: AsyncSession, task_id: int) -> TaskModel:
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
    result = await db.execute(
        select(TaskModel).where(TaskModel.id == task_id)
    )
    task = result.scalar_one_or_none()

    if not task:
        raise TaskNotFoundError(task_id)

    return task


async def create_task(db: AsyncSession, data: TaskCreate) -> TaskModel:
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
    await db.commit()
    await db.refresh(task)

    return task


async def list_tasks(
    db: AsyncSession,
    done: bool | None = None,
) -> list[TaskModel]:
    """
    List tasks, optionally filtered by completion status.

    Args:
        db (Session): Active SQLAlchemy database session.
        done (bool | None): Optional filter to return only
            completed or uncompleted tasks.

    Returns:
        list[TaskModel]: List of task ORM models.
    """
    query = select(TaskModel)

    if done is not None:
        query = query.where(TaskModel.done == done)

    result = await db.execute(query)
    return list(result.scalars().all())


async def complete_task(db: AsyncSession, task_id: int) -> TaskModel:
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
    result = await db.execute(
        update(TaskModel)
        .where(TaskModel.id == task_id, TaskModel.done.is_(False))
        .values(done=True)
    )

    if result.rowcount == 0:
        task = await get_task(db, task_id)
        if task.done:
            raise TaskAlreadyCompletedError()

    await db.commit()
    return await get_task(db, task_id)


async def update_task(
    db: AsyncSession,
    task_id: int,
    data: TaskUpdate | None,
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
    task = await get_task(db, task_id)

    if data is None:
        return task

    if task.done and data.done is False:
        raise InvalidTaskStateError(
            reason="Completed tasks cannot be reopened"
        )

    if data.title is not None:
        task.title = data.title

    if data.done is not None:
        task.done = data.done

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> None:
    """
    Delete a task.

    Args:
        db (Session): Active SQLAlchemy database session.
        task_id (int): Identifier of the task to be deleted.

    Raises:
        TaskNotFoundError: If the task does not exist (raised by get_task).
    """
    task = await get_task(db, task_id)

    await db.execute(delete(TaskModel).where(TaskModel.id == task_id))
    await db.commit()


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
