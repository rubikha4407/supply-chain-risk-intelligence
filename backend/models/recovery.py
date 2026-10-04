"""
RiskAssessment, ImpactAnalysis, RecoveryPlan, and RecoveryAction models.

- RiskAssessment: deterministic risk scoring output
- ImpactAnalysis: deterministic inventory/financial impact calculations
- RecoveryPlan & RecoveryAction: AI-reasoned recommendations + n8n execution tracking
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("external_events.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)

    # Deterministic risk scores
    risk_score = Column(Float, nullable=False)                # 0.0 – 1.0 (composite)
    geo_proximity_score = Column(Float, nullable=False)       # 0.0 – 1.0
    severity_score = Column(Float, nullable=False)            # 0.0 – 1.0
    supplier_criticality_score = Column(Float, nullable=False)  # 0.0 – 1.0
    inventory_vulnerability_score = Column(Float, nullable=False)  # 0.0 – 1.0

    # Deterministic estimates
    estimated_disruption_days = Column(Integer, nullable=True)
    inventory_runway_days = Column(Integer, nullable=True)
    shortage_starts_day = Column(Integer, nullable=True)

    # AI-generated explanation (populated by AI Recovery Reasoning layer)
    ai_risk_explanation = Column(Text, nullable=True)

    # Status
    status = Column(String, default="monitoring")  # monitoring|warning|critical|resolved
    assessed_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    event = relationship("ExternalEvent", back_populates="risk_assessments")
    supplier = relationship("Supplier", back_populates="risk_assessments")
    impact_analyses = relationship("ImpactAnalysis", back_populates="risk_assessment")
    recovery_plan = relationship(
        "RecoveryPlan", back_populates="risk_assessment", uselist=False,
    )

    def __repr__(self):
        return (
            f"<RiskAssessment {self.id}: Event {self.event_id}"
            f" → Supplier {self.supplier_id} (score={self.risk_score:.2f})>"
        )


class ImpactAnalysis(Base):
    __tablename__ = "impact_analyses"

    id = Column(Integer, primary_key=True, index=True)
    risk_assessment_id = Column(
        Integer, ForeignKey("risk_assessments.id"), nullable=False,
    )
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Deterministic impact calculations
    component_name = Column(String, nullable=False)
    units_at_risk = Column(Integer, nullable=False)
    revenue_at_risk = Column(Float, nullable=False)
    production_impact_pct = Column(Float, nullable=False)  # 0 – 100
    stockout_date = Column(DateTime, nullable=True)

    # AI-generated explanation
    ai_impact_explanation = Column(Text, nullable=True)

    # Relationships
    risk_assessment = relationship(
        "RiskAssessment", back_populates="impact_analyses",
    )
    product = relationship("Product", back_populates="impact_analyses")

    def __repr__(self):
        return (
            f"<ImpactAnalysis {self.id}: Product {self.product_id}"
            f" — {self.units_at_risk} units at risk>"
        )


class RecoveryPlan(Base):
    __tablename__ = "recovery_plans"

    id = Column(Integer, primary_key=True, index=True)
    risk_assessment_id = Column(
        Integer, ForeignKey("risk_assessments.id"), nullable=False,
    )
    plan_name = Column(String, nullable=False)
    status = Column(String, default="draft")  # draft|approved|executing|completed

    # AI-generated reasoning
    ai_reasoning = Column(Text, nullable=True)       # Why these actions were chosen
    ai_summary = Column(Text, nullable=True)          # Concise management summary

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    risk_assessment = relationship(
        "RiskAssessment", back_populates="recovery_plan",
    )
    actions = relationship("RecoveryAction", back_populates="plan")

    def __repr__(self):
        return f"<RecoveryPlan {self.id}: {self.plan_name} ({self.status})>"


class RecoveryAction(Base):
    __tablename__ = "recovery_actions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("recovery_plans.id"), nullable=False)

    action_type = Column(String, nullable=False)
    # switch_supplier | expedite_shipping | increase_inventory | notify_customer | halt_production

    description = Column(Text, nullable=False)
    priority = Column(Integer, default=1)  # 1 = highest priority

    # AI-generated explanation for why this specific action is recommended
    ai_rationale = Column(Text, nullable=True)

    # n8n execution tracking
    status = Column(String, default="pending")
    # pending | sent_to_n8n | in_progress | completed | failed
    n8n_workflow_id = Column(String, nullable=True)
    n8n_execution_id = Column(String, nullable=True)
    payload = Column(Text, nullable=True)  # JSON string sent to n8n

    sent_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    plan = relationship("RecoveryPlan", back_populates="actions")

    def __repr__(self):
        return (
            f"<RecoveryAction {self.id}: {self.action_type}"
            f" (priority={self.priority}, status={self.status})>"
        )
