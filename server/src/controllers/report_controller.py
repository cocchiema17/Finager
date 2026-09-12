from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/report", tags=["Report"])


@router.get("")
def download_report(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    excel_stream = AnalyticsService.generate_excel_report(db, user.id)

    headers = {
        "Content-Disposition": "attachment; filename=report.xlsx",
    }
    return StreamingResponse(
        excel_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )