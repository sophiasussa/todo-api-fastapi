from sqlalchemy.orm import Session

from app.models.task import TaskModel
from app.schemas.task import TaskCreate, TaskUpdate, Task
from app.exceptions.task import (
    InvalidTaskStateError,
    TaskNotFoundError,
    TaskAlreadyCompletedError,
)


def get_task(db: Session, task_id: int) -> TaskModel:
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()

    if not task:
        raise TaskNotFoundError(task_id)

    return task


def create_task(db: Session, data: TaskCreate) -> TaskModel:
    task = TaskModel(
        title=data.title,
        done=False,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    return task


def list_tasks(db: Session, done: bool | None = None) -> list[TaskModel]:
    query = db.query(TaskModel)

    if done is not None:
        query = query.filter(TaskModel.done == done)

    return query.all()


def complete_task(db: Session, task_id: int) -> TaskModel:
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
    task = get_task(db, task_id)

    db.delete(task)
    db.commit()


def to_domain(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        title=model.title,
        done=model.done,
    )
