from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Título da tarefa"
    )

class TaskUpdate(BaseModel):
    title: str | None = Field(
        None,
        min_length=3,
        max_length=100
    )
    done: bool | None = None

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

    class Config:
        from_attributes = True
