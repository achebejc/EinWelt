from typing import Any, Dict

from pydantic import BaseModel


class AnalyticsEventIn(BaseModel):
    event_name: str
    payload: Dict[str, Any] = {}
