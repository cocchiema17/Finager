from sqlalchemy import Column, Integer, BigInteger, String, DateTime, ForeignKey, UniqueConstraint, text, Uuid
from sqlalchemy.orm import relationship
from src.core.database import Base


class Space(Base):
    __tablename__ = "space"

    # BigInteger su PostgreSQL, Integer su SQLite per garantire autoincrement
    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    name = Column(String(40), nullable=False)
    userId = Column(Uuid(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    createdAt = Column(DateTime, server_default=text("CURRENT_TIMESTAMP"), nullable=False)

    __table_args__ = (
        UniqueConstraint("name", "userId", name="uq_space_name_user"),
    )

    # Relazioni
    user = relationship("User", back_populates="spaces")
    categories = relationship("Category", back_populates="space", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="space", cascade="all, delete-orphan")