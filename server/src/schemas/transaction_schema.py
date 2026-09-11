from datetime import date
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator


class TransactionCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=40)
    description: str = Field(..., min_length=1, max_length=200)
    date: date
    categoryName: str = Field(..., min_length=1, max_length=40)
    color: str = Field(..., min_length=1, max_length=40)
    spaceId: int
    value: float

    @field_validator("value")
    @classmethod
    def value_not_zero(cls, v: float) -> float:
        if v == 0:
            raise ValueError("Value cannot be 0")
        return v


class TransactionUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=40)
    description: str = Field(..., min_length=1, max_length=200)
    date: date
    value: float

    @field_validator("value")
    @classmethod
    def value_not_zero(cls, v: float) -> float:
        if v == 0:
            raise ValueError("Value cannot be 0")
        return v


class TransactionItemResponse(BaseModel):
    id: UUID
    title: str
    description: str
    type: str
    value: float
    categoryName: Optional[str] = None
    spaceId: int
    transactionDate: date
    spaceName: Optional[str] = None
    categoryColor: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class TransactionListResponse(BaseModel):
    totalElements: int
    totalPages: int
    value: list[TransactionItemResponse]