from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SpaceCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=40, description="Nome dello space")


class SpaceUpdate(BaseModel):
    name: str = Field(..., min_length=3, max_length=40, description="Nuovo nome dello space")


class SpaceResponse(BaseModel):
    id: int
    name: str
    userId: UUID
    createdAt: datetime

    model_config = ConfigDict(from_attributes=True)


class SpaceListResponse(BaseModel):
    value: list[SpaceResponse]