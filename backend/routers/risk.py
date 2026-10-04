"""
Risk assessment and dashboard API endpoints.
Provides aggregated KPIs, assessment lists, detailed assessment views,
and pipeline execution trigger.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.supplier import Supplier
from models.event import ExternalEvent
from models.inventory import Inventory
from models.recovery import RiskAssessment, RecoveryPlan, ImpactAnalysis
from schemas.recovery import DashboardKPIs, RiskAssessmentOut
from services.risk_engine import risk_engine

router = APIRouter(prefix="/api/risk", tags=["Risk & Impact"])


@router.get("/dashboard", response_model=DashboardKPIs)
def get_dashboard(db: Session = Depends(get_db)):
    """Aggregated risk overview KPIs."""
    total_suppliers = db.query(Supplier).count()

    at_risk = (
        db.query(RiskAssessment.supplier_id)
        .filter(RiskAssessment.status.in_(["warning", "critical"]))
        .distinct()
        .count()
    )

    active_events = (
        db.query(ExternalEvent).filter(ExternalEvent.is_active == True).count()  # noqa: E712
    )

    critical_alerts = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.status == "critical")
        .count()
    )

    inventories = db.query(Inventory).all()
    if inventories:
        avg_days = sum(inv.days_of_supply for inv in inventories) / len(inventories)
    else:
        avg_days = 0.0

    active_plans = (
        db.query(RecoveryPlan)
        .filter(RecoveryPlan.status.in_(["draft", "approved", "executing"]))
        .count()
    )

    return DashboardKPIs(
        total_suppliers=total_suppliers,
        at_risk_suppliers=at_risk,
        active_events=active_events,
        critical_alerts=critical_alerts,
        avg_inventory_days=round(avg_days, 1),
        active_recovery_plans=active_plans,
    )


@router.get("/assessments", response_model=list[RiskAssessmentOut])
def list_assessments(db: Session = Depends(get_db)):
    """List all risk assessments with impact analyses."""
    return (
        db.query(RiskAssessment)
        .options(
            joinedload(RiskAssessment.impact_analyses),
            joinedload(RiskAssessment.supplier),
            joinedload(RiskAssessment.event)
        )
        .order_by(RiskAssessment.risk_score.desc())
        .all()
    )


@router.get("/assessments/{assessment_id}", response_model=RiskAssessmentOut)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    """Get single risk assessment with impact analyses."""
    assessment = (
        db.query(RiskAssessment)
        .options(joinedload(RiskAssessment.impact_analyses))
        .filter(RiskAssessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    return assessment


@router.post("/analyze/{event_id}", response_model=list[RiskAssessmentOut])
def analyze_event_risks(event_id: int, db: Session = Depends(get_db)):
    """
    Trigger the complete 5-layer Risk Intelligence Pipeline for an external event.
    Returns generated risk assessments.
    """
    try:
        assessments = risk_engine.analyze_event(db, event_id)
        return assessments
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")


@router.get("/assessments/{assessment_id}/blast-radius")
def get_blast_radius(assessment_id: int, db: Session = Depends(get_db)):
    """Return the blast radius dependency graph for a risk assessment."""
    from models.product import Product
    
    assessment = (
        db.query(RiskAssessment)
        .options(
            joinedload(RiskAssessment.supplier),
            joinedload(RiskAssessment.event),
            joinedload(RiskAssessment.impact_analyses)
        )
        .filter(RiskAssessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")

    nodes = []
    edges = []

    # 1. Event Node
    event = assessment.event
    event_node_id = f"event_{event.id}"
    nodes.append({
        "id": event_node_id,
        "type": "customNode",
        "data": {
            "nodeType": "event",
            "title": event.title,
            "severity": event.severity,
            "type": event.event_type
        },
        "position": {"x": 250, "y": 0}
    })

    # 2. Supplier Node
    supplier = assessment.supplier
    supplier_node_id = f"supplier_{supplier.id}"
    nodes.append({
        "id": supplier_node_id,
        "type": "customNode",
        "data": {
            "nodeType": "supplier",
            "name": supplier.name,
            "country": supplier.country,
            "risk_score": assessment.risk_score,
            "status": assessment.status
        },
        "position": {"x": 250, "y": 150}
    })
    edges.append({"id": f"e_{event_node_id}_{supplier_node_id}", "source": event_node_id, "target": supplier_node_id, "animated": True, "style": {"stroke": "#f59e0b"}})

    # Fetch products
    product_ids = [ia.product_id for ia in assessment.impact_analyses]
    products = {p.id: p for p in db.query(Product).filter(Product.id.in_(product_ids)).all()} if product_ids else {}

    # 3. Component / Product / Inventory / Financial Nodes
    for i, ia in enumerate(assessment.impact_analyses):
        x_offset = i * 250
        
        comp_node_id = f"comp_{ia.id}"
        prod_node_id = f"prod_{ia.id}"
        inv_node_id = f"inv_{ia.id}"
        fin_node_id = f"fin_{ia.id}"
        
        # Component
        nodes.append({
            "id": comp_node_id,
            "type": "customNode",
            "data": {
                "nodeType": "component",
                "name": ia.component_name
            },
            "position": {"x": x_offset, "y": 300}
        })
        edges.append({"id": f"e_{supplier_node_id}_{comp_node_id}", "source": supplier_node_id, "target": comp_node_id})

        # Product
        prod_name = products.get(ia.product_id).name if ia.product_id in products else f"Product {ia.product_id}"
        nodes.append({
            "id": prod_node_id,
            "type": "customNode",
            "data": {
                "nodeType": "product",
                "name": prod_name
            },
            "position": {"x": x_offset, "y": 450}
        })
        edges.append({"id": f"e_{comp_node_id}_{prod_node_id}", "source": comp_node_id, "target": prod_node_id})

        # Inventory
        nodes.append({
            "id": inv_node_id,
            "type": "customNode",
            "data": {
                "nodeType": "inventory",
                "runway": assessment.inventory_runway_days,
                "disruption": assessment.estimated_disruption_days
            },
            "position": {"x": x_offset, "y": 600}
        })
        edges.append({"id": f"e_{prod_node_id}_{inv_node_id}", "source": prod_node_id, "target": inv_node_id})

        # Financial
        nodes.append({
            "id": fin_node_id,
            "type": "customNode",
            "data": {
                "nodeType": "financial",
                "revenue_at_risk": ia.revenue_at_risk,
                "production_impact": ia.production_impact_pct
            },
            "position": {"x": x_offset, "y": 750}
        })
        edges.append({"id": f"e_{inv_node_id}_{fin_node_id}", "source": inv_node_id, "target": fin_node_id, "animated": True, "style": {"stroke": "#ef4444"}})

    return {"nodes": nodes, "edges": edges}


@router.get("/assessments/{assessment_id}/explanation")
def get_risk_explanation(assessment_id: int, db: Session = Depends(get_db)):
    """Return the AI explanation for a risk assessment."""
    from services.ai_explainer import ai_explainer
    try:
        return ai_explainer.explain_risk(db, assessment_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

