from fastapi import APIRouter

# from app.Api.deps import get_current_user  # requires app.models.user
# from app.db.session import get_db  # requires models
# from app.models.analytics import AnalyticsEvent  # not yet implemented
# from app.models.user import User  # not yet implemented
# from app.schemas.analytics import AnalyticsEventIn  # not yet implemented

router = APIRouter()


@router.post("/events")
def create_event():
    return {"message": "Not implemented"}
