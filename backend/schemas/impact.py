"""
Pydantic schemas for Impact analysis.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ImpactAnalysisOut(BaseModel):
    id: int
    risk_assessment_id: int
    product_id: int
    component_name: str
    units_at_risk: int
    revenue_at_risk: float
    production_impact_pct: float
    stockout_date: Optional[datetime] = None
    ai_impact_explanation: Optional[str] = None

    model_config = {"from_attributes": True}
