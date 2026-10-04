"""
Pydantic schemas for Risk Assessment, Recovery Plan, and Recovery Action.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from schemas.impact import ImpactAnalysisOut
from schemas.event import EventOut
from schemas.supplier import SupplierOut


# ---------------------------------------------------------------------------
# Risk Assessment
# ---------------------------------------------------------------------------
class RiskAssessmentOut(BaseModel):
    id: int
    event_id: int
    supplier_id: int
    risk_score: float
    geo_proximity_score: float
    severity_score: float
    supplier_criticality_score: float
    inventory_vulnerability_score: float
    estimated_disruption_days: Optional[int] = None
    inventory_runway_days: Optional[int] = None
    shortage_starts_day: Optional[int] = None
    ai_risk_explanation: Optional[str] = None
    status: str
    assessed_at: datetime
    impact_analyses: list[ImpactAnalysisOut] = []
    
    # Adding for dashboard support
    supplier: Optional['SupplierOut'] = None
    event: Optional['EventOut'] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Recovery Action
# ---------------------------------------------------------------------------
class RecoveryActionOut(BaseModel):
    id: int
    plan_id: int
    action_type: str
    description: str
    priority: int
    ai_rationale: Optional[str] = None
    status: str
    n8n_workflow_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Recovery Plan
# ---------------------------------------------------------------------------
class RecoveryPlanOut(BaseModel):
    id: int
    risk_assessment_id: int
    plan_name: str
    status: str
    ai_reasoning: Optional[str] = None
    ai_summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    actions: list[RecoveryActionOut] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dashboard KPIs
# ---------------------------------------------------------------------------
class DashboardKPIs(BaseModel):
    total_suppliers: int
    at_risk_suppliers: int
    active_events: int
    critical_alerts: int
    avg_inventory_days: float
    active_recovery_plans: int
