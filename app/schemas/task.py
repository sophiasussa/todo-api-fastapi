from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    """
    Schema used to validate data when creating a new task.

    This model represents the payload expected by the API
    when a client wants to create a task.
    """

    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Title of the task"
    )


class TaskUpdate(BaseModel):
    """
    Schema used to validate data when updating an existing task.

    All fields are optional, allowing partial updates.
    """

    title: str | None = Field(
        None,
        min_length=3,
        max_length=100,
        description="Updated title of the task"
    )

    done: bool | None = Field(
        None,
        description="Indicates whether the task is completed"
    )


class TaskResponse(BaseModel):
    """
    Schema used to serialize task data returned by the API.

    This model defines the structure of task objects
    exposed to API consumers.
    """

    id: int
    title: str
    done: bool

    class Config:
        """
        Pydantic configuration.

        Enables compatibility with ORM models, allowing
        SQLAlchemy objects to be returned directly from services.
        """
        from_attributes = True
