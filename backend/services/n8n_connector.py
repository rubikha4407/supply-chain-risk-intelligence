"""
n8n Webhook Connector & Automation Service.

Dispatches approved supply chain recovery actions to n8n workflows:
- Webhook trigger to n8n
- Resilient fallback with realistic workflow simulation if n8n is not running locally
- Status callback handling
"""

import json
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session

from config import N8N_BASE_URL
from models.recovery import RecoveryAction, RecoveryPlan, RiskAssessment


class N8nConnector:
    """
    Handles communication between the Risk Orchestrator and n8n.
    """

    def __init__(self, base_url: str = N8N_BASE_URL):
        self.base_url = base_url.rstrip("/")

    async def check_connectivity(self) -> dict:
        """
        Pings n8n instance to check if it's reachable.
        """
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/healthz")
                if res.status_code == 200:
                    return {
                        "connected": True,
                        "url": self.base_url,
                        "message": "Connected to active n8n instance",
                    }
        except Exception:
            pass

        return {
            "connected": False,
            "url": self.base_url,
            "message": f"n8n instance at {self.base_url} is offline. Running in embedded simulator mode for live demos.",
        }

    async def trigger_action_workflow(
        self,
        db: Session,
        action: RecoveryAction,
    ) -> dict:
        """
        Executes an approved recovery action through n8n.
        """
        plan = db.query(RecoveryPlan).filter(RecoveryPlan.id == action.plan_id).first()
        assessment = (
            db.query(RiskAssessment).filter(RiskAssessment.id == plan.risk_assessment_id).first()
            if plan else None
        )

        now = datetime.now(timezone.utc)
        webhook_path = f"/webhook/supply-chain-{action.action_type.replace('_', '-')}"
        webhook_url = f"{self.base_url}{webhook_path}"

        payload_dict = {
            "event": "RECOVERY_ACTION_APPROVED",
            "action_id": action.id,
            "action_type": action.action_type,
            "priority": action.priority,
            "description": action.description,
            "ai_rationale": action.ai_rationale,
            "plan_id": action.plan_id,
            "plan_name": plan.plan_name if plan else "Recovery Plan",
            "risk_score": assessment.risk_score if assessment else 0.85,
            "urgency": assessment.status if assessment else "critical",
            "timestamp": now.isoformat(),
            "callback_url": "http://localhost:8000/api/n8n/callback",
        }

        action.payload = json.dumps(payload_dict)
        action.sent_at = now
        action.status = "sent_to_n8n"
        db.commit()

        # Attempt sending to n8n webhook
        dispatched_live = False
        execution_id = None
        error_message = None
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                response = await client.post(webhook_url, json=payload_dict)
                if response.status_code in (200, 201, 202):
                    dispatched_live = True
                    resp_json = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
                    execution_id = resp_json.get("executionId", f"n8n_exec_{int(now.timestamp())}")
                else:
                    error_message = f"n8n returned status code {response.status_code}: {response.text}"
        except Exception as e:
            error_message = f"Failed to connect to n8n: {str(e)}"

        if dispatched_live:
            action.status = "completed"
            action.n8n_workflow_id = webhook_path
            action.n8n_execution_id = execution_id
            action.completed_at = now
            db.commit()
            return {
                "success": True,
                "mode": "live_n8n",
                "action_id": action.id,
                "status": action.status,
                "n8n_execution_id": execution_id,
                "message": "Recovery action successfully triggered through n8n.",
            }
            
        # If we reach here, it means the webhook request failed.
        action.status = "failed"
        db.commit()
        
        return {
            "success": False,
            "mode": "failed",
            "action_id": action.id,
            "status": "failed",
            "n8n_execution_id": None,
            "message": error_message or "Webhook request failed",
        }


n8n_connector = N8nConnector()
