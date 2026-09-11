from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from src.repositories.space_repository import SpaceRepository
from src.repositories.transaction_repository import TransactionRepository
from src.schemas.transaction_schema import TransactionCreate, TransactionUpdate
from src.models.transaction import Transaction


class TransactionService:
    @staticmethod
    def create_transaction(db: Session, user_id: UUID, data: TransactionCreate) -> Transaction:
        # Verifica autorizzazione su Space
        space = SpaceRepository.get_by_id(db, data.spaceId)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found",
            )
        if space.userId != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add transactions to this space",
            )

        return TransactionRepository.create_atomic(
            db=db,
            title=data.title.strip(),
            description=data.description.strip(),
            tx_date=data.date,
            category_name=data.categoryName.strip(),
            color=data.color.strip(),
            space_id=data.spaceId,
            value=data.value,
        )

    @staticmethod
    def list_transactions(
        db: Session,
        user_id: UUID,
        page: int,
        page_size: int,
        space: Optional[str] = None,
        category_name: Optional[str] = None,
        search: Optional[str] = None,
        amount: Optional[float] = None,
        operator: Optional[str] = None,
        amount2: Optional[float] = None,
        sort_column: Optional[str] = None,
        asc: Optional[bool] = False,
    ) -> dict:
        total, pages, items = TransactionRepository.filter_user_transactions(
            db=db,
            user_id=user_id,
            page=page,
            pageSize=page_size,
            space_name=space,
            category_name=category_name,
            search=search,
            amount=amount,
            operator=operator,
            amount2=amount2,
            sort_column=sort_column,
            is_asc=bool(asc),
        )
        return {"totalElements": total, "totalPages": pages, "value": items}

    @staticmethod
    def update_transaction(db: Session, user_id: UUID, tx_id: UUID, data: TransactionUpdate) -> None:
        tx = TransactionRepository.get_user_transaction(db, tx_id, user_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        TransactionRepository.update(
            db=db,
            tx=tx,
            title=data.title.strip(),
            description=data.description.strip(),
            tx_date=data.date,
            value=data.value,
        )

    @staticmethod
    def delete_transaction(db: Session, user_id: UUID, tx_id: UUID) -> None:
        tx = TransactionRepository.get_user_transaction(db, tx_id, user_id)
        if not tx:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        TransactionRepository.delete(db, tx)