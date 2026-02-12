from app.exceptions.base import AppError


class TaskNotFoundError(AppError):
    def __init__(self, task_id: int | None = None):
        detail = (
            f"Task with id {task_id} was not found"
            if task_id is not None
            else "Task not found"
        )

        super().__init__(
            title="Task not found",
            detail=detail,
            status_code=404,
            error_code="TASK_NOT_FOUND",
            type_="https://api.todo.com/problems/TASK_NOT_FOUND",
        )


class TaskAlreadyCompletedError(AppError):
    def __init__(self):
        super().__init__(
            title="Task already completed",
            detail="Task is already completed",
            status_code=400,
            error_code="TASK_ALREADY_COMPLETED",
            type_="https://api.todo.com/problems/TASK_ALREADY_COMPLETED",
        )


class InvalidTaskStateError(AppError):
    def __init__(self, reason: str):
        super().__init__(
            title="Invalid task state",
            detail=reason,
            status_code=400,
            error_code="INVALID_TASK_STATE",
            type_="https://api.todo.com/problems/INVALID_TASK_STATE",
        )
