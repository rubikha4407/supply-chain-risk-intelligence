"""
n8n integration endpoints.
Provides connectivity checking, webhook callback receiver, and workflow configuration.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from database import get_db
from models.recovery import RecoveryAction
from services.n8n_connector import n8n_connector

router = APIRouter(prefix="/api/n8n", tags=["n8n Integration"])


@router.get("/status")
async def n8n_status():
    """Check n8n connectivity status."""
    return await n8n_connector.check_connectivity()


@router.post("/callback")
def n8n_callback(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
):
    """
    Webhook callback receiver called by n8n when a workflow execution completes.
    Updates the RecoveryAction status and audit log in the database.
    """
    action_id = payload.get("action_id")
    if not action_id:
        raise HTTPException(status_code=400, detail="Missing action_id in callback payload")

    action = db.query(RecoveryAction).filter(RecoveryAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail=f"RecoveryAction #{action_id} not found")

    action.status = payload.get("status", "completed")
    action.n8n_execution_id = payload.get("execution_id", action.n8n_execution_id)
    action.completed_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "success": True,
        "message": f"Action #{action_id} status updated to {action.status}",
        "action_id": action.id,
    }


@router.get("/workflows")
def list_workflows():
    """
    List available supply chain automation workflows configured for n8n.
    """
    return [
        {
            "id": "wf-supplier-switch",
            "name": "Alternate Supplier RFQ & PO Dispatch",
            "trigger": "POST /webhook/supply-chain-switch-supplier",
            "actions": [
                "Parse action payload",
                "Generate purchase requisition",
                "Send high-priority RFQ email to alternate supplier contact",
                "Log transaction in Google Sheets / ERP tracking table",
                "Send callback to Risk Orchestrator",
            ],
            "status": "active",
        },
        {
            "id": "wf-expedite-freight",
            "name": "Emergency Air Freight Logistics Booking",
            "trigger": "POST /webhook/supply-chain-expedite-shipping",
            "actions": [
                "Request expedited freight rate from DHL Global Forwarding",
                "Hold air cargo charter slot",
                "Notify logistics command center via Slack #supply-chain",
                "Update ETA in orchestration database",
            ],
            "status": "active",
        },
        {
            "id": "wf-customer-notification",
            "name": "Customer SLA & Delay Advisory Broadcast",
            "trigger": "POST /webhook/supply-chain-notify-customer",
            "actions": [
                "Identify impacted customer contracts and order backlog",
                "Draft personalized delay notice with mitigation timeline",
                "Submit to account executive for approval",
            ],
            "status": "active",
        },
    ]
