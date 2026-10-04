"""
Pydantic schemas for ExternalEvent request/response models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class EventBase(BaseModel):
    title: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: float = 200.0
    source_url: Optional[str] = None
    event_date: Optional[datetime] = None


class EventCreate(EventBase):
    """Used when manually ingesting an event. AI fields are populated by the pipeline."""
    pass


class EventOut(EventBase):
    id: int
    event_type: Optional[str] = None
    severity: Optional[str] = None
    affected_country: Optional[str] = None
    affected_region: Optional[str] = None
    ai_summary: Optional[str] = None
    ai_entities: Optional[str] = None
    detected_at: datetime
    is_active: bool

    model_config = {"from_attributes": True}


class SimulateEventRequest(BaseModel):
    """Request body for the /simulate/event endpoint."""
    title: str
    description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = None
