from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.schemas.transaction_schema import (
    TransactionCreate,
    TransactionUpdate,
    TransactionItemResponse,
    TransactionListResponse,
)
from src.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionListResponse)
def get_user_transactions(
    page: int = Query(default=0, ge=0),
    pageSize: int = Query(default=30, ge=1, le=500),
    space: Optional[str] = Query(default=None),
    categoryName: Optional[str] = Query(default=None),
    search: Optional[str] = Query(default=None),
    amount: Optional[float] = Query(default=None),
    operator: Optional[str] = Query(default=None),
    amount2: Optional[float] = Query(default=None),
    sortColumn: Optional[str] = Query(default=None),
    asc: Optional[bool] = Query(default=False),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TransactionService.list_transactions(
        db=db,
        user_id=user.id,
        page=page,
        page_size=pageSize,
        space=space,
        category_name=categoryName,
        search=search,
        amount=amount,
        operator=operator,
        amount2=amount2,
        sort_column=sortColumn,
        asc=asc,
    )


@router.post("", response_model=TransactionItemResponse, status_code=status.HTTP_201_CREATED)
def create_transaction(
    payload: TransactionCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return TransactionService.create_transaction(db, user.id, payload)


@router.patch("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def update_transaction(
    tx_id: UUID,
    payload: TransactionUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    TransactionService.update_transaction(db, user.id, tx_id, payload)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    tx_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    TransactionService.delete_transaction(db, user.id, tx_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)