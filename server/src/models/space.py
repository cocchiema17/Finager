from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.core.database import Base


class Space(Base):
    __tablename__ = "space"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(40), nullable=False)
    userId = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    createdAt = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "userId", name="uq_space_name_user"),
    )

    # Relazioni
    user = relationship("User", back_populates="spaces")
    categories = relationship("Category", back_populates="space", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="space", cascade="all, delete-orphan")