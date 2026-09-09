import enum
import uuid
from sqlalchemy import Column, String, Float, Date, BigInteger, ForeignKeyConstraint, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import relationship
from src.core.database import Base


class TransactionType(str, enum.Enum):
    revenue = "revenue"
    expense = "expense"


class Transaction(Base):
    __tablename__ = "transaction"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
    )
    title = Column(String(40), nullable=False)
    description = Column(String(200), nullable=False)
    type = Column(
        ENUM(TransactionType, name="transactiontype", create_type=False),
        nullable=False,
    )
    value = Column(Float, nullable=False)
    categoryName = Column(String(40), nullable=True)
    spaceId = Column(BigInteger, nullable=False)
    transactionDate = Column(Date, server_default=text("CURRENT_DATE"), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["categoryName", "spaceId"],
            ["category.name", "category.spaceId"],
            name="fk_transaction_category",
            ondelete="SET NULL",
        ),
    )

    # Relazioni
    space = relationship("Space", back_populates="transactions")
    category = relationship("Category", back_populates="transactions")