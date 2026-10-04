"""
Recovery plan API endpoints.
Handles listing recovery plans, plan generation, and action approval with n8n dispatch.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.recovery import RecoveryPlan, RecoveryAction
from schemas.recovery import RecoveryPlanOut, RecoveryActionOut
from services.recovery_planner import recovery_planner
from services.n8n_connector import n8n_connector
from services.whatif_simulator import whatif_simulator
from schemas.whatif import WhatIfRequest, StrategyOutcomeOut

router = APIRouter(prefix="/api/recovery", tags=["Recovery"])


@router.get("/plans", response_model=list[RecoveryPlanOut])
def list_plans(db: Session = Depends(get_db)):
    """List all recovery plans with actions."""
    return (
        db.query(RecoveryPlan)
        .options(joinedload(RecoveryPlan.actions))
        .order_by(RecoveryPlan.created_at.desc())
        .all()
    )


@router.get("/plans/{plan_id}", response_model=RecoveryPlanOut)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a single recovery plan with its actions."""
    plan = (
        db.query(RecoveryPlan)
        .options(joinedload(RecoveryPlan.actions))
        .filter(RecoveryPlan.id == plan_id)
        .first()
    )
    if not plan:
        raise HTTPException(status_code=404, detail="Recovery plan not found")
    return plan


@router.post("/plans/{assessment_id}/generate", response_model=RecoveryPlanOut)
def generate_plan(assessment_id: int, db: Session = Depends(get_db)):
    """
    Generate an AI-reasoned recovery plan for a specific risk assessment.
    """
    try:
        plan = recovery_planner.generate_plan_for_assessment(db, assessment_id)
        # Reload with actions
        return (
            db.query(RecoveryPlan)
            .options(joinedload(RecoveryPlan.actions))
            .filter(RecoveryPlan.id == plan.id)
            .first()
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recovery plan: {str(e)}")


@router.post("/actions/{action_id}/approve")
async def approve_recovery_action(action_id: int, db: Session = Depends(get_db)):
    """
    Approve a recovery action and trigger automated n8n workflow execution.
    """
    action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Recovery action not found")

    result = await n8n_connector.trigger_action_workflow(db, action)
    return result


@router.patch("/actions/{action_id}/status", response_model=RecoveryActionOut)
def update_action_status(
    action_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db),
):
    """
    Update status of a recovery action (can also be called by n8n callback).
    """
    action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Recovery action not found")

    action.status = status
    db.commit()
    db.refresh(action)
    return action


@router.post("/simulate", response_model=StrategyOutcomeOut)
def simulate_strategy(req: WhatIfRequest, db: Session = Depends(get_db)):
    """Simulate a single recovery strategy for a given risk assessment."""
    try:
        outcome = whatif_simulator.simulate_strategy(db, req.risk_assessment_id, req.strategy)
        return outcome
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compare", response_model=list[StrategyOutcomeOut])
def compare_strategies(assessment_id: int = Body(..., embed=True), db: Session = Depends(get_db)):
    """Compare all available recovery strategies for a given risk assessment."""
    try:
        outcomes = whatif_simulator.compare_strategies(db, assessment_id)
        return outcomes
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/explain-tradeoffs")
def explain_tradeoffs(strategies: list[dict] = Body(...)):
    from services.ai_explainer import ai_explainer
    return ai_explainer.explain_tradeoffs(strategies)
