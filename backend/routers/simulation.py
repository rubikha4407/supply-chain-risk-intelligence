"""
Simulation endpoints — interactive disruption simulator for demo mode.
Allows triggering pre-built scenarios or arbitrary disruption texts end-to-end.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models.event import ExternalEvent
from schemas.event import SimulateEventRequest
from services.risk_engine import risk_engine
from ml.event_classifier import event_classifier

router = APIRouter(prefix="/api/simulate", tags=["Simulation"])

PRESET_SCENARIOS = {
    "taiwan-typhoon": {
        "name": "Super Typhoon Gaemi (Taiwan Direct Landfall)",
        "description": "Category 5 Super Typhoon makes direct landfall near Hsinchu and Kaohsiung. Power grid disruption, port closures, and catastrophic flooding force TSMC fab closures and container terminal suspension.",
        "latitude": 24.8039,
        "longitude": 120.9647,
        "radius_km": 300.0,
        "expected_impact": "Halted MCU-7nm-A1 wafer fabrication; immediate line-down threat to SmartWidget Pro.",
    },
    "korean-semiconductor-fire": {
        "name": "Cleanroom Fire at Suwon Fabrication Facility",
        "description": "Electrical explosion causes extensive cleanroom fire and chemical contamination at Samsung Electronics Components facility in Suwon, halting DRAM and BLE-5.0 module packaging for 3-4 weeks.",
        "latitude": 37.2636,
        "longitude": 127.0286,
        "radius_km": 200.0,
        "expected_impact": "Memory and Bluetooth module shortage; impacts PowerBoard X and SensorArray Elite.",
    },
    "suez-blockage": {
        "name": "Ultra-Large Container Vessel Grounding in Suez Canal",
        "description": "Critical logistics artery blocked after 24,000 TEU container ship runs aground near Ismailia. Global maritime traffic between Asia and Europe suspended; 350+ vessels anchored.",
        "latitude": 30.4570,
        "longitude": 32.3510,
        "radius_km": 400.0,
        "expected_impact": "Severe maritime transit delays for transcontinental European shipments.",
    },
    "shenzhen-port-strike": {
        "name": "Shenzhen Port Terminal Worker Strike & Congestion",
        "description": "Labor dispute and equipment operators walkout paralyzes Yantian and Shekou container terminals in Shenzhen. Massive vessel backlog and 14-day cargo clearance delays.",
        "latitude": 22.5431,
        "longitude": 114.0579,
        "radius_km": 250.0,
        "expected_impact": "PCB and enclosure assembly delays across consumer product portfolio.",
    },
}


@router.get("/scenarios")
def list_scenarios():
    """List pre-built demo scenarios for interactive simulation."""
    return [
        {
            "id": s_id,
            "name": s["name"],
            "description": s["description"],
            "latitude": s["latitude"],
            "longitude": s["longitude"],
            "radius_km": s["radius_km"],
            "expected_impact": s["expected_impact"],
        }
        for s_id, s in PRESET_SCENARIOS.items()
    ]


@router.post("/scenarios/{scenario_id}/run")
def run_scenario(scenario_id: str, db: Session = Depends(get_db)):
    """
    Executes a pre-built simulation scenario end-to-end through the 5-layer pipeline:
    1. AI/NLP Event Understanding
    2. Deterministic Risk Engine
    3. Deterministic Impact Engine
    4. AI Recovery Reasoning Layer
    5. Action Generation for n8n
    """
    scenario = PRESET_SCENARIOS.get(scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found")

    # Ingest event into database
    nlp_res = event_classifier.understand_event(scenario["name"], scenario["description"])

    event = ExternalEvent(
        title=scenario["name"],
        description=scenario["description"],
        event_type=nlp_res["event_type"],
        severity=nlp_res["severity"],
        affected_country=nlp_res["affected_country"],
        affected_region=nlp_res["affected_region"],
        latitude=scenario["latitude"],
        longitude=scenario["longitude"],
        radius_km=scenario["radius_km"],
        ai_summary=nlp_res["ai_summary"],
        ai_entities=str(nlp_res["entities"]),
        event_date=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    # Run complete 5-layer pipeline
    assessments = risk_engine.analyze_event(db, event.id)

    return {
        "event_id": event.id,
        "title": event.title,
        "ai_understanding": {
            "event_type": event.event_type,
            "severity": event.severity,
            "affected_country": event.affected_country,
            "affected_region": event.affected_region,
            "ai_summary": event.ai_summary,
            "entities": nlp_res["entities"],
        },
        "assessments_count": len(assessments),
        "assessments": [
            {
                "id": a.id,
                "supplier_id": a.supplier_id,
                "risk_score": a.risk_score,
                "status": a.status,
                "inventory_runway_days": a.inventory_runway_days,
                "disruption_days": a.estimated_disruption_days,
                "ai_risk_explanation": a.ai_risk_explanation,
                "financial_impact": sum(ia.revenue_at_risk for ia in a.impact_analyses) if a.impact_analyses else 0.0,
                "inventory_impact": "Shortage expected" if a.inventory_runway_days and a.estimated_disruption_days and a.estimated_disruption_days > a.inventory_runway_days else "Sufficient",
                "recovery_recommendation": a.recovery_plan.ai_reasoning if a.recovery_plan else None,
                "explanation": a.ai_risk_explanation,
            }
            for a in assessments
        ],
    }


@router.post("/event")
def simulate_custom_event(data: SimulateEventRequest, db: Session = Depends(get_db)):
    """
    Ingests an arbitrary custom text event description and processes it through the pipeline.
    """
    nlp_res = event_classifier.understand_event(data.title, data.description)

    event = ExternalEvent(
        title=data.title,
        description=data.description,
        event_type=nlp_res["event_type"],
        severity=nlp_res["severity"],
        affected_country=nlp_res["affected_country"],
        affected_region=nlp_res["affected_region"],
        latitude=data.latitude or nlp_res["latitude"],
        longitude=data.longitude or nlp_res["longitude"],
        radius_km=data.radius_km or nlp_res["radius_km"],
        ai_summary=nlp_res["ai_summary"],
        ai_entities=str(nlp_res["entities"]),
        event_date=datetime.now(timezone.utc),
        is_active=True,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    assessments = risk_engine.analyze_event(db, event.id)

    return {
        "event_id": event.id,
        "title": event.title,
        "ai_understanding": {
            "event_type": event.event_type,
            "severity": event.severity,
            "affected_country": event.affected_country,
            "affected_region": event.affected_region,
            "ai_summary": event.ai_summary,
            "entities": nlp_res["entities"],
        },
        "assessments_count": len(assessments),
        "assessments": [
            {
                "id": a.id,
                "supplier_id": a.supplier_id,
                "risk_score": a.risk_score,
                "status": a.status,
                "inventory_runway_days": a.inventory_runway_days,
                "disruption_days": a.estimated_disruption_days,
                "ai_risk_explanation": a.ai_risk_explanation,
                "financial_impact": sum(ia.revenue_at_risk for ia in a.impact_analyses) if a.impact_analyses else 0.0,
                "inventory_impact": "Shortage expected" if a.inventory_runway_days and a.estimated_disruption_days and a.estimated_disruption_days > a.inventory_runway_days else "Sufficient",
                "recovery_recommendation": a.recovery_plan.ai_reasoning if a.recovery_plan else None,
                "explanation": a.ai_risk_explanation,
            }
            for a in assessments
        ],
    }
