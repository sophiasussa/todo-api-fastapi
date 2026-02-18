import pytest
from app.services.task_service import create_task, complete_task
from app.exceptions.task import TaskAlreadyCompletedError
from app.models.task import TaskModel
from app.schemas.task import TaskCreate


@pytest.mark.parametrize("already_done", [True, False])
def test_complete_task_service(db_session, already_done):
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
    task = create_task(
        db_session,
        TaskCreate(title="Service test")
    )

    assert task.id is not None
    assert task.title == "Service test"
    assert task.done is False


def test_complete_task_transaction_rollback(db_session):
    # task já concluída → vai lançar exceção
    task = TaskModel(title="Rollback", done=True)
    db_session.add(task)
    db_session.commit()

    with pytest.raises(TaskAlreadyCompletedError):
        complete_task(db_session, task.id)

    # garante que nada foi alterado
    db_session.refresh(task)
    assert task.done is True
