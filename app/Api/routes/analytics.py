import json

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.Api.deps import get_current_user
from app.db.session import get_db
from app.models.analytics import AnalyticsEvent
from app.models.user import User
from app.schemas.analytics import AnalyticsEventIn

router = APIRouter()


@router.post("/events", status_code=status.HTTP_201_CREATED)
def create_event(
    body: AnalyticsEventIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    event = AnalyticsEvent(
        user_id=current_user.id,
        event_name=body.event_name,
        payload_json=json.dumps(body.payload),
    )
    db.add(event)
    db.commit()
    return {"detail": "Event recorded."}
