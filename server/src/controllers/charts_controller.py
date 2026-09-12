from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.controllers.deps import get_current_user
from src.models.user import User
from src.schemas.analytics_schema import ChartsResponse
from src.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/charts", tags=["Charts"])


@router.get("", response_model=ChartsResponse)
def get_charts(
    spaceId: int = Query(..., description="ID dello space da analizzare"),
    fromDate: Optional[date] = Query(default=None),
    toDate: Optional[date] = Query(default=None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService.get_charts(
        db=db,
        user_id=user.id,
        space_id=spaceId,
        from_date=fromDate,
        to_date=toDate,
    )