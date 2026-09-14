from datetime import datetime, timezone
from typing import Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str = Field(..., min_length=1)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatSessionCreate(BaseModel):
    title: Optional[str] = Field(default="Nuova conversazione", max_length=100)


class ChatSessionResponse(BaseModel):
    id: str = Field(..., description="ID esadecimale della sessione (MongoDB ObjectId)")
    userId: UUID
    title: str
    createdAt: datetime
    updatedAt: datetime
    messages: list[ChatMessage] = []

    model_config = ConfigDict(from_attributes=True)


class ChatSessionSummary(BaseModel):
    """Rappresentazione leggera per la lista delle sessioni nella sidebar."""
    id: str
    userId: UUID
    title: str
    createdAt: datetime
    updatedAt: datetime
    messageCount: int = 0


class ChatPromptRequest(BaseModel):
    message: str = Field(..., min_length=1, description="Prompt dell'utente")