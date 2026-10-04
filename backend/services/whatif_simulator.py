"""
What-If Recovery Simulator Service.

Simulates different recovery strategies for an active risk assessment,
re-calculating estimated recovery time, cost, revenue at risk, and stockout projection.
"""

from typing import TypedDict
from sqlalchemy.orm import Session
from models.recovery import RiskAssessment
from models.supplier import AlternateSupplier
from services.impact_calculator import impact_calculator

class StrategyOutcome(TypedDict):
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


class WhatIfSimulator:
    def simulate_strategy(self, db: Session, assessment_id: int, strategy: str) -> StrategyOutcome:
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError("Risk assessment not found")

        disruption_days = assessment.estimated_disruption_days or 0
        supplier_id = assessment.supplier_id
        
        # Base outcome initialization
        recovery_time_days = disruption_days
        additional_cost = 0.0
        
        # Strategy modifications
        if strategy == "do_nothing":
            description = "No intervention. Absorb the disruption."
            feasibility = "High"
            
        elif strategy == "switch_supplier":
            alt_supplier = db.query(AlternateSupplier).filter(AlternateSupplier.primary_supplier_id == supplier_id).first()
            if alt_supplier:
                recovery_time_days = int(alt_supplier.lead_time_days)
                # arbitrary estimate for cost: assuming 100 units * cost multiplier * $100 average price
                additional_cost = alt_supplier.cost_multiplier * 50000 
                description = f"Switch to {alt_supplier.component_name} alternate supplier."
                feasibility = "Medium"
            else:
                description = "Switch supplier (No predefined alternate found - estimated)."
                recovery_time_days = min(disruption_days, 14)
                additional_cost = 100000.0
                feasibility = "Low"

        elif strategy == "expedite_shipment":
            recovery_time_days = max(1, int(disruption_days * 0.6))  # 40% time reduction
            additional_cost = 25000.0  # Assumed premium freight
            description = "Use emergency air freight to reduce transit time."
            feasibility = "High"

        elif strategy == "alternate_route":
            recovery_time_days = max(1, int(disruption_days * 0.7))  # 30% time reduction
            additional_cost = 15000.0
            description = "Reroute shipments around blocked nodes."
            feasibility = "Medium"

        elif strategy == "reduce_production":
            recovery_time_days = disruption_days
            additional_cost = 0.0
            description = "Reduce production rate by 30% to stretch inventory."
            feasibility = "High"
        else:
            raise ValueError("Unknown strategy")

        # Recalculate impact using the new recovery_time_days
        # If reduce_production, we would ideally stretch runway. We can hack this by passing a smaller disruption to simulate the stretched runway absorbing it.
        effective_disruption = recovery_time_days
        if strategy == "reduce_production":
            # If we reduce production by 30%, inventory lasts ~42% longer (1 / 0.7 = 1.42).
            # This is equivalent to facing a smaller disruption relative to current inventory.
            effective_disruption = int(effective_disruption * 0.7)

        impact = impact_calculator.calculate_supplier_impact(db, supplier_id, effective_disruption)
        
        shortage_days = max(0, effective_disruption - impact["min_inventory_runway_days"])
        stockout_status = "YES" if shortage_days > 0 else "NO"
        
        # If reduce production, there is an inherent production impact (e.g. 30%), we ensure it reflects this
        prod_impact = impact["highest_production_impact_pct"]
        if strategy == "reduce_production":
            prod_impact = max(prod_impact, 30.0)
            
        # Also, reduce_production incurs opportunity cost for the units not produced
        if strategy == "reduce_production" and impact["total_revenue_at_risk"] == 0:
            additional_cost += 10000.0 # arbitrary opportunity cost

        return {
            "strategy": strategy,
            "description": description,
            "recovery_time_days": recovery_time_days,
            "additional_cost": additional_cost,
            "shortage_duration_days": shortage_days,
            "units_at_risk": impact["total_units_at_risk"],
            "revenue_at_risk": impact["total_revenue_at_risk"],
            "production_impact_pct": prod_impact,
            "stockout_status": stockout_status,
            "feasibility": feasibility
        }
        
    def compare_strategies(self, db: Session, assessment_id: int) -> list[StrategyOutcome]:
        strategies = [
            "do_nothing",
            "switch_supplier",
            "expedite_shipment",
            "alternate_route",
            "reduce_production"
        ]
        return [self.simulate_strategy(db, assessment_id, s) for s in strategies]

whatif_simulator = WhatIfSimulator()
