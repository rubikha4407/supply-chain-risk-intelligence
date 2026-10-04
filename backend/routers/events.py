"""
External Event API endpoints.
Manages event feeds, single event inspection, and automated ingestion processing.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.event import ExternalEvent
from schemas.event import EventOut, EventCreate
from ml.event_classifier import event_classifier
from services.risk_engine import risk_engine

router = APIRouter(prefix="/api/events", tags=["Events"])


@router.get("", response_model=list[EventOut])
def list_events(
    event_type: str | None = None,
    severity: str | None = None,
    active_only: bool = False,
    db: Session = Depends(get_db),
):
    """List external events with optional filters."""
    query = db.query(ExternalEvent)
    if active_only:
        query = query.filter(ExternalEvent.is_active == True)  # noqa: E712
    if event_type:
        query = query.filter(ExternalEvent.event_type == event_type)
    if severity:
        query = query.filter(ExternalEvent.severity == severity)
    return query.order_by(ExternalEvent.detected_at.desc()).all()


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """Get a single event by ID."""
    event = db.query(ExternalEvent).filter(ExternalEvent.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=EventOut, status_code=201)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    """
    Manually ingest an event.
    Applies the AI/NLP Event Understanding layer to extract signals and entities,
    then triggers the risk engine analysis.
    """
    nlp_res = event_classifier.understand_event(data.title, data.description)

    event_data = data.model_dump()
    event_data["event_type"] = nlp_res["event_type"]
    event_data["severity"] = nlp_res["severity"]
    event_data["affected_country"] = nlp_res["affected_country"]
    event_data["affected_region"] = nlp_res["affected_region"]
    if not event_data.get("latitude") and nlp_res["latitude"]:
        event_data["latitude"] = nlp_res["latitude"]
        event_data["longitude"] = nlp_res["longitude"]
        event_data["radius_km"] = nlp_res["radius_km"]
    event_data["ai_summary"] = nlp_res["ai_summary"]
    event_data["ai_entities"] = str(nlp_res["entities"])

    event = ExternalEvent(**event_data)
    db.add(event)
    db.commit()
    db.refresh(event)

    # Trigger risk analysis
    try:
        risk_engine.analyze_event(db, event.id)
    except Exception as e:
        print(f"Warning: automatic risk analysis failed: {e}")

    return event
