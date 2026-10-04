"""
Recovery Planner Service.

Generates structured Recovery Plans and ranked Recovery Actions
using the AI Recovery Reasoning Layer and deterministic impact data.
"""

from sqlalchemy.orm import Session

from models.recovery import RiskAssessment, ImpactAnalysis, RecoveryPlan, RecoveryAction
from models.supplier import Supplier, AlternateSupplier
from models.event import ExternalEvent
from ml.recovery_reasoner import recovery_reasoner
from services.impact_calculator import impact_calculator


class RecoveryPlanner:
    """
    Coordinates creation of Recovery Plans, Action items, and AI rationale.
    """

    def generate_plan_for_assessment(
        self,
        db: Session,
        assessment_id: int,
    ) -> RecoveryPlan:
        # Check if plan already exists for this assessment
        existing_plan = (
            db.query(RecoveryPlan)
            .filter(RecoveryPlan.risk_assessment_id == assessment_id)
            .first()
        )
        if existing_plan:
            return existing_plan

        assessment = db.query(RiskAssessment).filter(RiskAssessment.id == assessment_id).first()
        if not assessment:
            raise ValueError(f"RiskAssessment #{assessment_id} not found")

        supplier = db.query(Supplier).filter(Supplier.id == assessment.supplier_id).first()
        event = db.query(ExternalEvent).filter(ExternalEvent.id == assessment.event_id).first()

        # Run or load impact analysis
        impact_summary = impact_calculator.calculate_supplier_impact(
            db=db,
            supplier_id=supplier.id,
            disruption_days=assessment.estimated_disruption_days or 14,
        )

        # Store ImpactAnalysis records if not already stored
        existing_impacts = (
            db.query(ImpactAnalysis)
            .filter(ImpactAnalysis.risk_assessment_id == assessment.id)
            .all()
        )
        if not existing_impacts:
            for c in impact_summary["component_impacts"]:
                ia = ImpactAnalysis(
                    risk_assessment_id=assessment.id,
                    product_id=c["product_id"],
                    component_name=c["component_name"],
                    units_at_risk=c["units_at_risk"],
                    revenue_at_risk=c["revenue_at_risk"],
                    production_impact_pct=c["production_impact_pct"],
                    stockout_date=c["stockout_date"],
                    ai_impact_explanation=(
                        f"Stockout after {c['inventory_runway_days']} days. "
                        f"Disruption duration {c['disruption_days']} days leaves a {c['shortage_days']}-day deficit."
                    ),
                )
                db.add(ia)
            db.commit()

        # Query alternate suppliers
        alts = (
            db.query(AlternateSupplier)
            .filter(AlternateSupplier.primary_supplier_id == supplier.id)
            .all()
        )
        alt_list = []
        for a in alts:
            alt_sup = db.query(Supplier).filter(Supplier.id == a.alternate_supplier_id).first()
            if alt_sup:
                alt_list.append({
                    "name": alt_sup.name,
                    "component": a.component_name,
                    "cost_multiplier": a.cost_multiplier,
                    "lead_time_days": a.lead_time_days,
                })

        # Critical components and impacted products list
        critical_comps = [
            c["component_name"] for c in impact_summary["component_impacts"] if c["is_critical"]
        ]
        impacted_prods = list({
            c["product_name"] for c in impact_summary["component_impacts"] if c["units_at_risk"] > 0
        })

        stockout_str = (
            impact_summary["earliest_stockout_date"].strftime("%b %d, %Y")
            if impact_summary["earliest_stockout_date"]
            else "Day 8"
        )

        # Generate AI Recovery Reasoning
        reasoning = recovery_reasoner.generate_reasoning(
            supplier_name=supplier.name,
            supplier_country=supplier.country,
            event_title=event.title if event else "Disruption Event",
            event_type=event.event_type if event else "supply_chain",
            severity=event.severity if event else "high",
            proximity_km=assessment.geo_proximity_score * 100.0,
            disruption_days=impact_summary["disruption_days"],
            inventory_runway_days=impact_summary["min_inventory_runway_days"],
            earliest_stockout_str=stockout_str,
            total_units_at_risk=impact_summary["total_units_at_risk"],
            total_revenue_at_risk=impact_summary["total_revenue_at_risk"],
            critical_components=critical_comps,
            impacted_products=impacted_prods,
            alternate_suppliers=alt_list,
        )

        # Update RiskAssessment with AI explanation and deterministic runway
        assessment.ai_risk_explanation = reasoning["ai_risk_explanation"]
        assessment.inventory_runway_days = impact_summary["min_inventory_runway_days"]
        assessment.shortage_starts_day = impact_summary["min_inventory_runway_days"]
        db.commit()

        # Create RecoveryPlan
        plan = RecoveryPlan(
            risk_assessment_id=assessment.id,
            plan_name=f"Rapid Mitigation: {supplier.name} Disruption",
            status="draft",
            ai_reasoning=reasoning["recommended_action_rationale"],
            ai_summary=reasoning["ai_summary"],
        )
        db.add(plan)
        db.flush()

        # Create RecoveryActions based on comparisons
        for comp in reasoning["action_comparisons"]:
            action = RecoveryAction(
                plan_id=plan.id,
                action_type=comp["action_type"],
                description=comp["title"],
                priority=comp["priority"],
                ai_rationale=comp["tradeoff_analysis"],
                status="pending",
            )
            db.add(action)

        db.commit()
        db.refresh(plan)
        return plan


recovery_planner = RecoveryPlanner()
