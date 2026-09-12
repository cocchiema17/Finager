from datetime import date
from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.models.transaction import Transaction
from src.models.category import Category
from src.models.space import Space


class AnalyticsRepository:
    @staticmethod
    def get_bar_chart_data(
        db: Session,
        space_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[dict]:
        year_col = func.extract("year", Transaction.transactionDate).label("year")
        month_col = func.extract("month", Transaction.transactionDate).label("month")

        query = (
            db.query(
                Transaction.type,
                func.count(Transaction.id).label("count"),
                func.abs(func.sum(Transaction.value)).label("total"),
                year_col,
                month_col,
            )
            .filter(Transaction.spaceId == space_id)
        )

        if from_date:
            query = query.filter(Transaction.transactionDate >= from_date)
        if to_date:
            query = query.filter(Transaction.transactionDate <= to_date)

        rows = (
            query.group_by(Transaction.type, year_col, month_col)
            .order_by(year_col, month_col)
            .all()
        )

        return [
            {
                "type": r.type.value if hasattr(r.type, "value") else str(r.type),
                "count": int(r.count),
                "total": float(r.total or 0.0),
                "year": int(r.year),
                "month": int(r.month),
            }
            for r in rows
        ]

    @staticmethod
    def get_pie_chart_data(
        db: Session,
        space_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[dict]:
        query = (
            db.query(
                Transaction.categoryName,
                Category.color,
                func.count(Transaction.id).label("count"),
            )
            .join(
                Category,
                (Transaction.categoryName == Category.name) & (Transaction.spaceId == Category.spaceId),
            )
            .filter(Transaction.spaceId == space_id)
        )

        if from_date:
            query = query.filter(Transaction.transactionDate >= from_date)
        if to_date:
            query = query.filter(Transaction.transactionDate <= to_date)

        rows = (
            query.group_by(Transaction.categoryName, Category.color)
            .order_by(func.count(Transaction.id).desc())
            .all()
        )

        return [
            {
                "categoryName": r.categoryName,
                "color": r.color,
                "count": int(r.count),
            }
            for r in rows
        ]

    @staticmethod
    def get_line_chart_data(
        db: Session,
        space_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> list[dict]:
        """
        Calcola il saldo progressivo cumulato per mese/anno.
        Raggruppiamo prima a livello mensile, poi calcoliamo la somma cumulata.
        """
        year_col = func.extract("year", Transaction.transactionDate).label("year")
        month_col = func.extract("month", Transaction.transactionDate).label("month")

        query = (
            db.query(
                year_col,
                month_col,
                func.sum(Transaction.value).label("monthly_sum"),
            )
            .filter(Transaction.spaceId == space_id)
        )

        if from_date:
            query = query.filter(Transaction.transactionDate >= from_date)
        if to_date:
            query = query.filter(Transaction.transactionDate <= to_date)

        monthly_records = (
            query.group_by(year_col, month_col)
            .order_by(year_col.asc(), month_col.asc())
            .all()
        )

        cumulative_results = []
        running_total = 0.0
        for record in monthly_records:
            running_total += float(record.monthly_sum or 0.0)
            cumulative_results.append({
                "year": int(record.year),
                "month": int(record.month),
                "value": round(running_total, 2),
            })

        return cumulative_results

    @staticmethod
    def get_report_data(db: Session, user_id: UUID) -> list[dict]:
        rows = (
            db.query(
                Transaction.title.label("Title"),
                Transaction.description.label("Description"),
                Transaction.value.label("Amount"),
                Transaction.categoryName.label("Category"),
                Transaction.transactionDate.label("Date"),
            )
            .join(Space, Transaction.spaceId == Space.id)
            .filter(Space.userId == user_id)
            .order_by(Transaction.transactionDate.desc())
            .all()
        )

        return [
            {
                "Title": r.Title,
                "Description": r.Description,
                "Amount": r.Amount,
                "Category": r.Category or "",
                "Date": str(r.Date),
            }
            for r in rows
        ]