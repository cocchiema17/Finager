from datetime import date
from uuid import UUID
from sqlalchemy import func
from sqlalchemy.orm import Session
from src.models.space import Space
from src.models.transaction import Transaction


class FinancialContextService:
    @staticmethod
    def build_user_financial_context(db: Session, user_id: UUID, recent_limit: int = 25) -> str:
        """
        Estrae da PostgreSQL un riepilogo strutturato della situazione finanziaria
        dell'utente (Spaces, totali entrate/uscite, ripartizione per categoria e movimenti recenti)
        da iniettare nel System Prompt dell'LLM.
        """
        spaces = db.query(Space).filter(Space.userId == user_id).all()

        if not spaces:
            return (
                "DATI FINANZIARI DELL'UTENTE:\n"
                "L'utente non ha ancora creato alcuno Space né registrato transazioni."
            )

        space_map = {s.id: s.name for s in spaces}
        space_ids = list(space_map.keys())

        # 1. Calcolo entrate, uscite e saldo per singolo Space
        space_totals_rows = (
            db.query(
                Transaction.spaceId,
                func.sum(Transaction.value).label("net_balance"),
                func.count(Transaction.id).label("tx_count"),
            )
            .filter(Transaction.spaceId.in_(space_ids))
            .group_by(Transaction.spaceId)
            .all()
        )
        totals_by_space = {
            row.spaceId: (float(row.net_balance or 0.0), int(row.tx_count))
            for row in space_totals_rows
        }

        lines = [
            f"DATA ODIERNA DI RIFERIMENTO: {date.today().isoformat()}",
            "=== RIEPILOGO SPACES E SALDI ===",
        ]

        global_balance = 0.0
        for s in spaces:
            balance, count = totals_by_space.get(s.id, (0.0, 0))
            global_balance += balance
            lines.append(f"- Space '{s.name}': Saldo attuale = {balance:.2f} EUR ({count} transazioni)")

        lines.append(f"SALDO COMPLESSIVO TOTALE: {global_balance:.2f} EUR\n")

        # 2. Ripartizione aggregata per Categoria e Tipo (Entrata / Uscita)
        category_rows = (
            db.query(
                Transaction.categoryName,
                Transaction.type,
                func.count(Transaction.id).label("count"),
                func.sum(Transaction.value).label("total"),
            )
            .filter(Transaction.spaceId.in_(space_ids))
            .group_by(Transaction.categoryName, Transaction.type)
            .order_by(func.abs(func.sum(Transaction.value)).desc())
            .all()
        )

        if category_rows:
            lines.append("=== TOTALI PER CATEGORIA ===")
            for r in category_rows:
                tx_type = r.type.value if hasattr(r.type, "value") else str(r.type)
                cat_label = r.categoryName or "Senza categoria"
                lines.append(
                    f"- Categoria '{cat_label}' ({tx_type}): {float(r.total or 0.0):.2f} EUR ({r.count} movimenti)"
                )
            lines.append("")

        # 3. Ultimi N movimenti cronologici
        recent_txs = (
            db.query(Transaction)
            .filter(Transaction.spaceId.in_(space_ids))
            .order_by(Transaction.transactionDate.desc(), Transaction.id.desc())
            .limit(recent_limit)
            .all()
        )

        if recent_txs:
            lines.append(f"=== ULTIME {len(recent_txs)} TRANSAZIONI RECENTI ===")
            for tx in recent_txs:
                s_name = space_map.get(tx.spaceId, "N/D")
                cat_name = tx.categoryName or "Nessuna"
                desc_part = f" ({tx.description})" if tx.description else ""
                lines.append(
                    f"- [{tx.transactionDate}] {tx.title}{desc_part}: {tx.value:+.2f} EUR | Categoria: {cat_name} | Space: {s_name}"
                )

        return "\n".join(lines)