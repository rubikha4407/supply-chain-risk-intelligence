"""
ExternalEvent model — represents an external disruption event
(weather, geopolitical, port congestion, supplier issue, transport disruption).
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text,
)
from sqlalchemy.orm import relationship

from database import Base


class ExternalEvent(Base):
    __tablename__ = "external_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    # AI-extracted fields (populated by AI/NLP Event Understanding layer)
    event_type = Column(String, nullable=True)     # weather|geopolitical|port|supplier|transport
    severity = Column(String, nullable=True)        # low|medium|high|critical
    affected_country = Column(String, nullable=True)
    affected_region = Column(String, nullable=True)
    ai_summary = Column(Text, nullable=True)        # AI-generated concise summary
    ai_entities = Column(Text, nullable=True)       # JSON string of extracted entities

    # Location
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    radius_km = Column(Float, default=200.0)

    # Metadata
    source_url = Column(String, nullable=True)
    event_date = Column(DateTime, nullable=True)
    detected_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
    )
    is_active = Column(Boolean, default=True)

    # Relationships
    risk_assessments = relationship("RiskAssessment", back_populates="event")

    def __repr__(self):
        return f"<ExternalEvent {self.id}: {self.title} ({self.event_type}/{self.severity})>"
