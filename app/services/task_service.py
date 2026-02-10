from asyncio import Task
from app.model.task import TaskModel


def to_domain(model: TaskModel) -> Task:
    return Task(
        id=model.id,
        title=model.title,
        done=model.done,
    )
