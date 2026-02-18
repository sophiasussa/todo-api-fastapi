from app.exceptions.base import AppError


class TaskNotFoundError(AppError):
    """
    Error raised when a task is not found in the system.

    Optionally receives the task identifier to enrich
    the error message returned to the client.
    """

    def __init__(self, task_id: int | None = None):
        """
        Initializes the task not found error.

        Args:
            task_id (int | None): Identifier of the task that was not found.
                When provided, it is included in the error message.
        """
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
    """
    Error raised when an operation is performed on a task
    that has already been completed.
    """

    def __init__(self):
        """
        Initializes the task already completed error.
        """
        super().__init__(
            title="Task already completed",
            detail="Task is already completed",
            status_code=400,
            error_code="TASK_ALREADY_COMPLETED",
            type_="https://api.todo.com/problems/TASK_ALREADY_COMPLETED",
        )


class InvalidTaskStateError(AppError):
    """
    Error raised when an invalid transition or operation
    is attempted on the current task state.
    """

    def __init__(self, reason: str):
        """
        Initializes the invalid task state error.

        Args:
            reason (str): Specific description of why
                the task state is considered invalid.
        """
        super().__init__(
            title="Invalid task state",
            detail=reason,
            status_code=400,
            error_code="INVALID_TASK_STATE",
            type_="https://api.todo.com/problems/INVALID_TASK_STATE",
        )
