from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=40)
    spaceId: int
    color: Optional[str] = Field(default="#000000", max_length=40)


class CategoryResponse(BaseModel):
    name: str
    spaceId: int
    color: Optional[str] = None
    spaceName: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CategoryListResponse(BaseModel):
    value: list[CategoryResponse]