import uuid
from sqlalchemy import Column, String, DateTime, text, Uuid
from sqlalchemy.orm import relationship
from src.core.database import Base


class User(Base):
    __tablename__ = "user"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    firstName = Column(String(30), nullable=False)
    lastName = Column(String(30), nullable=False)
    email = Column(String(60), nullable=False, unique=True, index=True)
    password = Column(String(200), nullable=False)
    createdAt = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    # Relazioni
    spaces = relationship("Space", back_populates="user", cascade="all, delete-orphan")