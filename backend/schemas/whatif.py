from pydantic import BaseModel

class WhatIfRequest(BaseModel):
    risk_assessment_id: int
    strategy: str

class StrategyOutcomeOut(BaseModel):
    strategy: str
    description: str
    recovery_time_days: int
    additional_cost: float
    shortage_duration_days: int
    units_at_risk: int
    revenue_at_risk: float
    production_impact_pct: float
    stockout_status: str
    feasibility: str
