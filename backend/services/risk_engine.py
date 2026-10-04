"""
Risk Engine Orchestrator.

Wires all 5 stages together:
1. AI/NLP Event Understanding
2. Deterministic Risk Engine
3. Deterministic Impact Engine
4. AI Recovery Reasoning Layer
5. Recovery Plan & n8n Action Generation
"""

import json
from sqlalchemy.orm import Session

from models.event import ExternalEvent
from models.supplier import Supplier, AlternateSupplier
from models.product import BillOfMaterials
from models.inventory import Inventory
from models.recovery import RiskAssessment
from ml.event_classifier import event_classifier
from ml.geo_matcher import calculate_geo_proximity
from ml.duration_estimator import estimate_disruption_days
from ml.risk_scorer import calculate_risk_score
from services.impact_calculator import impact_calculator
from services.recovery_planner import recovery_planner


class RiskEngine:
    """
    Complete pipeline orchestrator for supply chain risk assessment.
    """

    def analyze_event(self, db: Session, event_id: int) -> list[RiskAssessment]:
        """
        Runs the full risk intelligence pipeline on an ingested event.
        """
        event = db.query(ExternalEvent).filter(ExternalEvent.id == event_id).first()
        if not event:
            raise ValueError(f"Event #{event_id} not found")

        # -------------------------------------------------------------
        # Stage 1: AI/NLP Event Understanding (if not already extracted)
        # -------------------------------------------------------------
        if not event.event_type or not event.severity or not event.ai_summary:
            nlp_res = event_classifier.understand_event(event.title, event.description)
            event.event_type = nlp_res["event_type"]
            event.severity = nlp_res["severity"]
            event.affected_country = nlp_res["affected_country"]
            event.affected_region = nlp_res["affected_region"]
            if nlp_res["latitude"] and (not event.latitude or event.latitude == 0.0):
                event.latitude = nlp_res["latitude"]
                event.longitude = nlp_res["longitude"]
                event.radius_km = nlp_res["radius_km"]
            event.ai_summary = nlp_res["ai_summary"]
            event.ai_entities = json.dumps(nlp_res["entities"])
            db.commit()

        # Disruption duration estimation (deterministic)
        disruption_days = estimate_disruption_days(event.event_type, event.severity)

        # -------------------------------------------------------------
        # Stage 2: Deterministic Risk Engine across all active suppliers
        # -------------------------------------------------------------
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()  # noqa: E712
        assessments: list[RiskAssessment] = []

        for sup in suppliers:
            # Geographic proximity (Haversine formula)
            geo_res = calculate_geo_proximity(
                event_lat=event.latitude,
                event_lon=event.longitude,
                event_radius_km=event.radius_km or 250.0,
                supplier_lat=sup.latitude,
                supplier_lon=sup.longitude,
                event_country=event.affected_country,
                supplier_country=sup.country,
            )

            # Skip suppliers completely unaffected (distance > 4x radius and different country)
            if not geo_res["is_in_range"] and geo_res["proximity_score"] <= 0.05:
                continue

            # Deterministic supplier properties
            has_crit_bom = (
                db.query(BillOfMaterials)
                .filter(
                    BillOfMaterials.supplier_id == sup.id,
                    BillOfMaterials.is_critical == True,  # noqa: E712
                )
                .count() > 0
            )

            has_alts = (
                db.query(AlternateSupplier)
                .filter(AlternateSupplier.primary_supplier_id == sup.id)
                .count() > 0
            )

            # Inventory stock calculation
            inv_records = db.query(Inventory).filter(Inventory.supplier_id == sup.id).all()
            if inv_records:
                min_days_supply = min(inv.days_of_supply for inv in inv_records)
            else:
                min_days_supply = 15.0

            # Deterministic score
            score_data = calculate_risk_score(
                severity=event.severity,
                geo_proximity_score=geo_res["proximity_score"],
                tier=sup.tier,
                has_critical_bom=has_crit_bom,
                has_alternates=has_alts,
                reliability_score=sup.reliability_score,
                min_days_of_supply=min_days_supply,
            )

            # Check if assessment exists
            assessment = (
                db.query(RiskAssessment)
                .filter(
                    RiskAssessment.event_id == event.id,
                    RiskAssessment.supplier_id == sup.id,
                )
                .first()
            )

            if not assessment:
                assessment = RiskAssessment(
                    event_id=event.id,
                    supplier_id=sup.id,
                    risk_score=score_data["risk_score"],
                    geo_proximity_score=score_data["geo_proximity_score"],
                    severity_score=score_data["severity_score"],
                    supplier_criticality_score=score_data["supplier_criticality_score"],
                    inventory_vulnerability_score=score_data["inventory_vulnerability_score"],
                    estimated_disruption_days=disruption_days,
                    inventory_runway_days=int(min_days_supply),
                    shortage_starts_day=int(min_days_supply),
                    status=score_data["status"],
                )
                db.add(assessment)
                db.flush()
            else:
                assessment.risk_score = score_data["risk_score"]
                assessment.geo_proximity_score = score_data["geo_proximity_score"]
                assessment.severity_score = score_data["severity_score"]
                assessment.supplier_criticality_score = score_data["supplier_criticality_score"]
                assessment.inventory_vulnerability_score = score_data["inventory_vulnerability_score"]
                assessment.estimated_disruption_days = disruption_days
                assessment.status = score_data["status"]
                db.flush()

            # -------------------------------------------------------------
            # Stage 3 & 4: Deterministic Impact & AI Recovery Reasoning
            # -------------------------------------------------------------
            # For critical or warning risks, generate recovery plan & detailed impact
            if assessment.status in ("critical", "warning"):
                recovery_planner.generate_plan_for_assessment(db, assessment.id)

            assessments.append(assessment)

        db.commit()
        return assessments


risk_engine = RiskEngine()
