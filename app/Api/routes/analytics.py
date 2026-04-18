import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.Api.deps import get_current_user
from app.db.session import get_db
from app.models.analytics import AnalyticsEvent
from app.models.user import User
from app.schemas.analytics import AnalyticsEventIn

router = APIRouter()

@router.post("/events")
def create_event(
    payload: AnalyticsEventIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    event = AnalyticsEvent(
        user_id=current_user.id,
        event_name=payload.event_name,
        payload_json=json.dumps(payload.payload or {}),
    )
    db.add(event)
    db.commit()
    return {"message": "event stored"}
