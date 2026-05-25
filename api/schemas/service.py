from uuid import UUID

from pydantic import BaseModel


class ServiceOut(BaseModel):
    id: UUID
    name: str
    price: float
    duration: int
    description: str | None = None
