from sqlalchemy import Column, Integer, String, Boolean
from app.database.base import Base


class TaskModel(Base):
    """
    ORM model representing the `tasks` table in the database.

    This model is used by SQLAlchemy to map records from the `tasks` table
    to Python objects. It serves as the single source of truth for the
    persisted task structure.
    """

    __tablename__ = "tasks"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        doc="Unique identifier of the task"
    )

    title = Column(
        String(100),
        nullable=False,
        doc="Task title (between 3 and 100 characters)"
    )

    done = Column(
        Boolean,
        default=False,
        doc="Indicates whether the task has been completed"
    )
