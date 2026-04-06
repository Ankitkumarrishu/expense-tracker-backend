from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import DashboardUser
from app.database import get_db
from app.schemas.summary import DashboardSummary, PeriodTrend
from app.services import summary_service

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary(
    user: DashboardUser,
    db: Annotated[Session, Depends(get_db)],
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
    recent_limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be on or before date_to",
        )
    return summary_service.build_dashboard_summary(
        db,
        viewer_role=user.role,
        date_from=date_from,
        date_to=date_to,
        recent_limit=recent_limit,
    )


@router.get("/trends", response_model=list[PeriodTrend])
def dashboard_trends(
    user: DashboardUser,
    db: Annotated[Session, Depends(get_db)],
    granularity: Annotated[Literal["month", "week"], Query()] = "month",
    date_from: Annotated[date | None, Query()] = None,
    date_to: Annotated[date | None, Query()] = None,
):
    if date_from is not None and date_to is not None and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="date_from must be on or before date_to",
        )
    return summary_service.build_trends(
        db,
        granularity=granularity,
        date_from=date_from,
        date_to=date_to,
    )
