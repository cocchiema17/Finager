from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# Schema per la registrazione di un nuovo utente
class UserRegister(BaseModel):
    firstName: str = Field(..., min_length=1, max_length=30)
    lastName: str = Field(..., min_length=1, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)


# Schema per il login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Schema restituito dall'API (omettiamo la password hashata)
class UserResponse(BaseModel):
    id: UUID
    firstName: str
    lastName: str
    email: EmailStr
    createdAt: datetime

    class Config:
        from_attributes = True  # Permette a Pydantic di leggere oggetti ORM di SQLAlchemy