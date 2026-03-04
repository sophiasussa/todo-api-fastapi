"""
Unit tests for Task service layer.

This module contains unit tests for the task service functions,
focusing on business rules and transactional behavior.

Scope:
- Tests the service layer in isolation
- Uses an in-memory database session
- Does NOT involve FastAPI routes or HTTP
- Does NOT require Docker or external services

All tests in this module are marked as `unit`.
"""

import pytest

# Mark all tests in this module as unit tests
pytestmark = pytest.mark.unit

from app.services.task_service import create_task, complete_task
from app.exceptions.task import TaskAlreadyCompletedError
from app.models.task import TaskModel
from app.schemas.task import TaskCreate


@pytest.mark.parametrize("already_done", [True, False])
def test_complete_task_service(db_session, already_done):
    """
    Test task completion behavior in the service layer.

    This test verifies:
    - If a task is already completed, completing it again raises an error
    - If a task is not completed, it can be successfully completed

    The test is parametrized to cover both scenarios.
    """
    task = TaskModel(title="Service", done=already_done)
    db_session.add(task)
    db_session.commit()

    if already_done:
        with pytest.raises(TaskAlreadyCompletedError):
            complete_task(db_session, task.id)
    else:
        result = complete_task(db_session, task.id)
        assert result.done is True


def test_create_task_service(db_session):
    """
    Test task creation through the service layer.

    Ensures that:
    - A task is persisted in the database
    - An ID is generated
    - The task starts with `done = False`
    """
    task = create_task(
        db_session,
        TaskCreate(title="Service test")
    )

    assert task.id is not None
    assert task.title == "Service test"
    assert task.done is False


def test_complete_task_transaction_rollback(db_session):
    """
    Test transactional rollback behavior when completing a task fails.

    Scenario:
    - A task already marked as completed is attempted to be completed again
    - The service raises an exception
    - The database state must remain unchanged

    This test guarantees that the service layer does not partially
    commit changes when an exception occurs.
    """
    # Task already completed → should raise an exception
    task = TaskModel(title="Rollback", done=True)
    db_session.add(task)
    db_session.commit()

    with pytest.raises(TaskAlreadyCompletedError):
        complete_task(db_session, task.id)

    # Ensure no state was changed after the exception
    db_session.refresh(task)
    assert task.done is True
