"""
AI Explanation and Strategy Comparison Service.
Provides deterministic, backend-driven, AI-like explanations based on calculated metrics,
satisfying the requirement to avoid hallucinations and always reflect true calculated values.
"""

from typing import TypedDict
from sqlalchemy.orm import Session
from models.recovery import RiskAssessment

class AIExplanation(TypedDict):
    why_it_matters: str
    business_impact: str

class StrategyTradeoffs(TypedDict):
    comparison_explanation: str

class AIExplainer:
    def explain_risk(self, db: Session, assessment_id: int) -> AIExplanation:
        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError("Assessment not found")
        
        supplier = assessment.supplier
        event = assessment.event
        
        # 1. Why it matters
        why = (
            f"{supplier.name} is classified as {assessment.status.upper()} because the supplier is located "
            f"inside the affected region of the {event.severity.upper()} event ('{event.title}'). "
            f"Current inventory covers only {assessment.inventory_runway_days or 0} days while the "
            f"estimated disruption is {assessment.estimated_disruption_days or 0} days."
        )
        
        # 2. Business impact
        total_rev = sum(ia.revenue_at_risk for ia in assessment.impact_analyses)
        max_prod = max([ia.production_impact_pct for ia in assessment.impact_analyses] or [0])
        
        impact = (
            f"WHAT HAPPENED: {event.title} in {event.affected_country or 'the region'}.\n"
            f"WHY IT MATTERS: A critical supply node is halted. Buffer inventory is insufficient to cover the gap.\n"
            f"WHAT COULD HAPPEN: We project a stockout in {assessment.inventory_runway_days or 0} days, "
            f"leading to a {max_prod}% production hit and ${total_rev:,.2f} in revenue at risk.\n"
            f"WHAT OPTIONS ARE AVAILABLE: We can expedite shipments, switch to alternate suppliers, or reduce production to stretch runway."
        )
        
        return {
            "why_it_matters": why,
            "business_impact": impact
        }
        
    def explain_tradeoffs(self, strategies: list[dict]) -> StrategyTradeoffs:
        if not strategies:
            return {"comparison_explanation": "No strategies provided for comparison."}
            
        do_nothing = next((s for s in strategies if s['strategy'] == 'do_nothing'), None)
        switch = next((s for s in strategies if s['strategy'] == 'switch_supplier'), None)
        expedite = next((s for s in strategies if s['strategy'] == 'expedite_shipment'), None)
        reduce_prod = next((s for s in strategies if s['strategy'] == 'reduce_production'), None)
        
        parts = []
        if do_nothing:
            parts.append(f"Doing nothing results in a baseline recovery time of {do_nothing['recovery_time_days']} days and ${do_nothing['revenue_at_risk']:,.0f} revenue at risk.")
            
        if switch:
            parts.append(
                f"Switching suppliers requires an additional procurement cost of ${switch['additional_cost']:,.0f}, "
                f"resulting in a recovery time of {switch['recovery_time_days']} days."
            )
            
        if expedite:
            parts.append(
                f"Expediting the shipment costs ${expedite['additional_cost']:,.0f} but heavily reduces "
                f"recovery time to {expedite['recovery_time_days']} days, dropping revenue at risk to ${expedite['revenue_at_risk']:,.0f}."
            )
            
        if reduce_prod:
            parts.append(
                f"Reducing production incurs no direct logistics cost but guarantees a {reduce_prod['production_impact_pct']}% "
                f"production slowdown to stretch existing inventory."
            )
            
        explanation = " ".join(parts)
        explanation += " The final decision should weigh the immediate cash layout against the protected revenue."
        
        return {"comparison_explanation": explanation}

ai_explainer = AIExplainer()
