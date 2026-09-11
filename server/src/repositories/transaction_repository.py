import math
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from src.models.transaction import Transaction, TransactionType
from src.models.space import Space
from src.models.category import Category


class TransactionRepository:
    @staticmethod
    def get_by_id(db: Session, tx_id: UUID) -> Optional[Transaction]:
        return db.query(Transaction).filter(Transaction.id == tx_id).first()

    @staticmethod
    def get_user_transaction(db: Session, tx_id: UUID, user_id: UUID) -> Optional[Transaction]:
        return (
            db.query(Transaction)
            .join(Space, Transaction.spaceId == Space.id)
            .filter(Transaction.id == tx_id, Space.userId == user_id)
            .first()
        )

    @staticmethod
    def create_atomic(
        db: Session,
        title: str,
        description: str,
        tx_date,
        category_name: str,
        color: str,
        space_id: int,
        value: float,
    ) -> Transaction:
        # 1. Inserimento categoria idempotente (se non esiste già)
        category = (
            db.query(Category)
            .filter(Category.name == category_name, Category.spaceId == space_id)
            .first()
        )
        if not category:
            category = Category(name=category_name, spaceId=space_id, color=color)
            db.add(category)
            db.flush()  # Assicura che la riga sia inserita prima del riferimento FK

        # 2. Inserimento transazione
        tx_type = TransactionType.revenue if value > 0 else TransactionType.expense
        tx = Transaction(
            title=title,
            description=description,
            type=tx_type,
            value=value,
            categoryName=category_name,
            spaceId=space_id,
            transactionDate=tx_date,
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def filter_user_transactions(
        db: Session,
        user_id: UUID,
        page: int = 0,
        pageSize: int = 30,
        space_name: Optional[str] = None,
        category_name: Optional[str] = None,
        search: Optional[str] = None,
        amount: Optional[float] = None,
        operator: Optional[str] = None,
        amount2: Optional[float] = None,
        sort_column: Optional[str] = None,
        is_asc: bool = False,
    ) -> tuple[int, int, list[dict]]:
        # Query base con JOIN su Space e Category
        query = (
            db.query(
                Transaction,
                Space.name.label("spaceName"),
                Category.color.label("categoryColor"),
            )
            .join(Space, Transaction.spaceId == Space.id)
            .outerjoin(
                Category,
                (Transaction.categoryName == Category.name) & (Transaction.spaceId == Category.spaceId),
            )
            .filter(Space.userId == user_id)
        )

        # Filtri dinamici
        if space_name:
            query = query.filter(Space.name == space_name)
        if category_name:
            query = query.filter(Transaction.categoryName == category_name)
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Transaction.title.ilike(search_pattern),
                    Transaction.description.ilike(search_pattern),
                )
            )

        # Operatori sull'importo
        if operator and amount is not None:
            op = operator.upper()
            if op == "EQ":
                query = query.filter(Transaction.value == amount)
            elif op == "NE":
                query = query.filter(Transaction.value != amount)
            elif op == "GT":
                query = query.filter(Transaction.value > amount)
            elif op == "GE":
                query = query.filter(Transaction.value >= amount)
            elif op == "LT":
                query = query.filter(Transaction.value < amount)
            elif op == "LE":
                query = query.filter(Transaction.value <= amount)
            elif op == "BT" and amount2 is not None:
                query = query.filter(Transaction.value >= amount, Transaction.value <= amount2)

        # Conteggio totale
        total_elements = query.count()
        total_pages = math.ceil(total_elements / pageSize) if pageSize > 0 else 0

        # Ordinamento
        order_direction = asc if is_asc else desc
        col_map = {
            "title": Transaction.title,
            "description": Transaction.description,
            "amount": Transaction.value,
            "space": Space.name,
            "category": Transaction.categoryName,
            "date": Transaction.transactionDate,
            "transactionDate": Transaction.transactionDate,
        }
        order_col = col_map.get(sort_column or "transactionDate", Transaction.transactionDate)
        query = query.order_by(order_direction(order_col))

        # Paginazione
        results = query.offset(page * pageSize).limit(pageSize).all()

        formatted_items = []
        for tx, s_name, c_color in results:
            formatted_items.append({
                "id": tx.id,
                "title": tx.title,
                "description": tx.description,
                "type": tx.type.value if hasattr(tx.type, "value") else str(tx.type),
                "value": tx.value,
                "categoryName": tx.categoryName,
                "spaceId": tx.spaceId,
                "transactionDate": tx.transactionDate,
                "spaceName": s_name,
                "categoryColor": c_color,
            })

        return total_elements, total_pages, formatted_items

    @staticmethod
    def update(db: Session, tx: Transaction, title: str, description: str, tx_date, value: float) -> Transaction:
        tx.title = title
        tx.description = description
        tx.transactionDate = tx_date
        tx.value = value
        tx.type = TransactionType.revenue if value > 0 else TransactionType.expense
        db.commit()
        db.refresh(tx)
        return tx

    @staticmethod
    def delete(db: Session, tx: Transaction) -> None:
        db.delete(tx)
        db.commit()