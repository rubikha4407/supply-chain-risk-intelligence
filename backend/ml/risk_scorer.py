"""
Deterministic Risk Engine.

Calculates composite supplier risk scores using an explainable mathematical formula:
Risk = (0.30 * Severity) + (0.25 * Proximity) + (0.25 * Criticality) + (0.20 * Inventory Vulnerability)

All weights and formulas are strictly deterministic — not opaque ML.
"""

from typing import TypedDict


class RiskScoreBreakdown(TypedDict):
    risk_score: float
    severity_score: float
    geo_proximity_score: float
    supplier_criticality_score: float
    inventory_vulnerability_score: float
    status: str
    formula_explanation: str


SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 1.0,
    "high": 0.75,
    "medium": 0.50,
    "low": 0.25,
}


def compute_severity_score(severity: str) -> float:
    return SEVERITY_WEIGHTS.get(severity.lower(), 0.50)


def compute_supplier_criticality(
    tier: str,
    has_critical_bom: bool,
    has_alternates: bool,
    reliability_score: float,
) -> float:
    """
    Computes supplier criticality factor (0.0 to 1.0):
    - Tier 1 base: 0.45, Tier 2 base: 0.25
    - Supplies mission-critical component: +0.35
    - Sole source (no qualified alternate supplier): +0.20
    - Historical supplier unreliability penalty: up to +0.10
    """
    base = 0.45 if tier.lower() == "tier 1" else 0.25

    if has_critical_bom:
        base += 0.35

    if not has_alternates:
        base += 0.20

    # Low reliability increases criticality risk
    unreliability = max(0.0, (1.0 - reliability_score) * 0.25)
    base += unreliability

    return round(min(1.0, max(0.1, base)), 3)


def compute_inventory_vulnerability(min_days_of_supply: float) -> float:
    """
    Computes inventory vulnerability factor (0.0 to 1.0):
    Fewer days of stock = higher vulnerability.
    Under 7 days = severe vulnerability (> 0.75)
    Over 30 days = low vulnerability (< 0.10)
    """
    if min_days_of_supply <= 0:
        return 1.0

    # Vulnerability decreases linearly to 0 as days reach 30
    vuln = 1.0 - min(min_days_of_supply / 30.0, 1.0)
    return round(max(0.05, vuln), 3)


def calculate_risk_score(
    severity: str,
    geo_proximity_score: float,
    tier: str,
    has_critical_bom: bool,
    has_alternates: bool,
    reliability_score: float,
    min_days_of_supply: float,
) -> RiskScoreBreakdown:
    """
    Deterministic Risk Engine calculation.
    """
    severity_score = compute_severity_score(severity)
    criticality_score = compute_supplier_criticality(
        tier=tier,
        has_critical_bom=has_critical_bom,
        has_alternates=has_alternates,
        reliability_score=reliability_score,
    )
    vulnerability_score = compute_inventory_vulnerability(min_days_of_supply)

    # Weighted deterministic formula
    w_sev = 0.30
    w_geo = 0.25
    w_crit = 0.25
    w_vuln = 0.20

    raw_score = (
        (w_sev * severity_score)
        + (w_geo * geo_proximity_score)
        + (w_crit * criticality_score)
        + (w_vuln * vulnerability_score)
    )

    final_score = round(min(1.0, max(0.0, raw_score)), 3)

    if final_score >= 0.65:
        status = "critical"
    elif final_score >= 0.40:
        status = "warning"
    else:
        status = "monitoring"

    explanation = (
        f"Deterministic Calculation: "
        f"0.30*(Severity={severity_score}) + "
        f"0.25*(Proximity={geo_proximity_score}) + "
        f"0.25*(Criticality={criticality_score}) + "
        f"0.20*(Vulnerability={vulnerability_score}) = "
        f"{final_score:.3f} [{status.upper()}]"
    )

    return {
        "risk_score": final_score,
        "severity_score": severity_score,
        "geo_proximity_score": geo_proximity_score,
        "supplier_criticality_score": criticality_score,
        "inventory_vulnerability_score": vulnerability_score,
        "status": status,
        "formula_explanation": explanation,
    }
