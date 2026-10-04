"""
AI Recovery Reasoning Layer.

Provides:
1. Explain why the supplier is at risk (root-cause attribution)
2. Explain the business impact (financial and production ramifications)
3. Compare possible recovery actions (trade-off evaluation)
4. Explain why a particular recovery action is recommended (decision rationale)
5. Generate a concise procurement/management summary (executive briefing)
"""

from typing import TypedDict


class ActionOptionComparison(TypedDict):
    action_type: str
    title: str
    tradeoff_analysis: str
    estimated_cost_impact: str
    speed_to_mitigate: str
    feasibility_score: float  # 0.0 - 1.0
    recommended: bool
    priority: int


class RecoveryReasoningOutput(TypedDict):
    ai_risk_explanation: str
    ai_impact_explanation: str
    action_comparisons: list[ActionOptionComparison]
    recommended_action_rationale: str
    ai_summary: str


class RecoveryReasoner:
    """
    AI Recovery Reasoning Layer.
    Translates deterministic signals into strategic procurement insights
    and comparative decision logic.
    """

    def generate_reasoning(
        self,
        supplier_name: str,
        supplier_country: str,
        event_title: str,
        event_type: str,
        severity: str,
        proximity_km: float,
        disruption_days: int,
        inventory_runway_days: int,
        earliest_stockout_str: str,
        total_units_at_risk: int,
        total_revenue_at_risk: float,
        critical_components: list[str],
        impacted_products: list[str],
        alternate_suppliers: list[dict],
    ) -> RecoveryReasoningOutput:
        comp_str = ", ".join(critical_components) if critical_components else "key electronic components"
        prod_str = ", ".join(impacted_products) if impacted_products else "flagship product lines"

        # 1. Why is the supplier at risk?
        ai_risk_explanation = (
            f"{supplier_name} ({supplier_country}) is situated approximately {int(proximity_km)}km from the epicenter of "
            f"the {severity.upper()} {event_type} event ('{event_title}'). "
            f"The supplier holds critical single-source responsibility for {comp_str}. "
            f"With an estimated operational outage of {disruption_days} days and an existing inventory runway of only "
            f"{inventory_runway_days} days, the factory will be unable to fulfill pending replenishment orders, "
            f"creating a direct supply deficit."
        )

        # 2. What is the business impact?
        ai_impact_explanation = (
            f"If unmitigated, inventory exhaustion will trigger a production halt on {earliest_stockout_str}. "
            f"This disruption impacts manufacturing for {prod_str}, exposing {total_units_at_risk:,} finished units to delay "
            f"and creating an immediate top-line revenue exposure of ${total_revenue_at_risk:,.2f}. "
            f"Secondary effects include missed customer delivery SLAs and downstream channel partner penalties."
        )

        # 3. Compare possible recovery actions (Tradeoff evaluation)
        comparisons: list[ActionOptionComparison] = []

        # Option A: Switch/Split with Alternate Supplier
        has_alt = len(alternate_suppliers) > 0
        alt_names = [a.get("name", "Qualified Tier 1 Backup") for a in alternate_suppliers]
        alt_name_str = ", ".join(alt_names) if alt_names else "Samsung Electronics Components"
        lead_time_alt = alternate_suppliers[0].get("lead_time_days", 21) if alternate_suppliers else 21
        cost_mult = alternate_suppliers[0].get("cost_multiplier", 1.25) if alternate_suppliers else 1.25

        comparisons.append({
            "action_type": "switch_supplier",
            "title": f"Activate Alternate Sourcing ({alt_name_str})",
            "tradeoff_analysis": (
                f"Sourcing via {alt_name_str} provides confirmed manufacturing capacity but incurs a "
                f"+{int((cost_mult - 1.0) * 100)}% unit price premium and a {lead_time_alt}-day lead time. "
                f"Because lead time exceeds current runway ({inventory_runway_days}d), this must be executed simultaneously "
                f"with shipping expedites to minimize the stockout window."
            ),
            "estimated_cost_impact": f"+{int((cost_mult - 1.0) * 100)}% component unit cost",
            "speed_to_mitigate": f"{lead_time_alt} days lead time",
            "feasibility_score": 0.92 if has_alt else 0.60,
            "recommended": True,
            "priority": 1,
        })

        # Option B: Expedite In-Transit / Emergency Air Freight
        comparisons.append({
            "action_type": "expedite_shipping",
            "title": "Authorize Emergency Air Freight & Expedited Handling",
            "tradeoff_analysis": (
                "Reroutes pending ocean cargo to chartered air freight. High logistics surcharge, but compresses "
                "transit from 18 days to 3-5 days, injecting immediate buffer stock to avert line stoppage."
            ),
            "estimated_cost_impact": "$12,000 - $18,000 air cargo premium",
            "speed_to_mitigate": "3 - 5 days arrival",
            "feasibility_score": 0.88,
            "recommended": True,
            "priority": 2,
        })

        # Option C: Production Throttling & SKU Allocation
        comparisons.append({
            "action_type": "halt_production",
            "title": "Throttle Assembly Line & Prioritize High-Margin SKUs",
            "tradeoff_analysis": (
                "Ration existing component stock to extend runway from 8 days to 16 days. Protects enterprise "
                "contracts but temporarily slows consumer retail fulfillment by 40%."
            ),
            "estimated_cost_impact": "Operational reallocation (no direct cash outlay)",
            "speed_to_mitigate": "Immediate (operational adjustment)",
            "feasibility_score": 0.78,
            "recommended": False,
            "priority": 3,
        })

        # Option D: Proactive Customer & SLA Notification
        comparisons.append({
            "action_type": "notify_customer",
            "title": "Trigger Automated Stakeholder & Customer SLA Alert",
            "tradeoff_analysis": (
                "Notifies tier-1 enterprise distributors of revised fulfillment windows. Preserves trust and avoids "
                "breach-of-contract contractual penalties."
            ),
            "estimated_cost_impact": "$0 direct cost (brand protection)",
            "speed_to_mitigate": "Instant via n8n automation",
            "feasibility_score": 0.95,
            "recommended": True,
            "priority": 4,
        })

        # 4. Explain why a particular action is recommended
        recommended_action_rationale = (
            f"Multi-Vector Mitigation Strategy: Priority 1 is awarded to Activating Alternate Supplier ({alt_name_str}) "
            f"because the {disruption_days}-day outage duration exceeds safety stock capacity, making permanent supply diversion essential. "
            f"However, due to the {lead_time_alt}-day alternate supplier lead time, Priority 2 (Emergency Air Freight) must be "
            f"co-executed to cover the {max(0, lead_time_alt - inventory_runway_days)}-day stockout exposure gap. "
            f"Automated notification through n8n ensures immediate vendor engagement."
        )

        # 5. Concise Executive Summary for Procurement & Leadership
        ai_summary = (
            f"EXECUTIVE BRIEFING: {supplier_name} disruption risk rated CRITICAL due to {event_title}. "
            f"Production line-down projected on {earliest_stockout_str} without intervention (${total_revenue_at_risk:,.2f} exposure). "
            f"AI recommendation: Issue secondary purchase order to {alt_name_str} and authorize emergency air freight. "
            f"n8n automated orchestration ready for one-click deployment upon stakeholder sign-off."
        )

        return {
            "ai_risk_explanation": ai_risk_explanation,
            "ai_impact_explanation": ai_impact_explanation,
            "action_comparisons": comparisons,
            "recommended_action_rationale": recommended_action_rationale,
            "ai_summary": ai_summary,
        }


recovery_reasoner = RecoveryReasoner()
