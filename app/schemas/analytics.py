from typing import Any, Dict

from pydantic import BaseModel, Field


class AnalyticsEventIn(BaseModel):
    """Payload for recording a client-side analytics event."""

    event_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Dot-namespaced event identifier, e.g. 'screen.view'",
        examples=["screen.view"],
    )
    payload: Dict[str, Any] = Field(
        default={},
        description="Arbitrary JSON metadata attached to the event",
    )

