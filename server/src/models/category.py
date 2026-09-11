from sqlalchemy import Column, String, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from src.core.database import Base


class Category(Base):
    __tablename__ = "category"

    name = Column(String(40), primary_key=True)
    spaceId = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        ForeignKey("space.id", ondelete="CASCADE"),
        primary_key=True
    )
    color = Column(String(40), nullable=True)

    # Relazioni
    space = relationship("Space", back_populates="categories")
    transactions = relationship("Transaction", back_populates="category", overlaps="space,transactions")