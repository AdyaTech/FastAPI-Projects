from typing import Literal

from pydantic import BaseModel, Field, field_validator


class MenuItem(BaseModel):
    id: int
    name: str
    category: str
    price: float
    description: str
    available: bool
    color: str
    vegan: bool
    sweetness: int
    tags: list[str]


class MenuResponse(BaseModel):
    status: str = "success"
    count: int
    items: list[MenuItem]


# ---------- Flavor Lab (AI) ----------

class CupItem(BaseModel):
    id: int
    name: str
    category: str
    price: float
    color: str
    why: str


class Cup(BaseModel):
    source: Literal["groq", "local"]  # groq = real AI model, local = offline taste matcher
    name: str
    note: str
    items: list[CupItem]  # bottom scoop first, topper last
    total: float


class Turn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(max_length=400)


class ComposeRequest(BaseModel):
    message: str = Field(max_length=300)
    history: list[Turn] = Field(default_factory=list, max_length=12)

    @field_validator("message")
    @classmethod
    def at_least_a_few_characters(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Write at least 3 characters")
        return value


class AIStatus(BaseModel):
    mode: Literal["groq", "local"]
    model: str | None = None
