"""
Deterministic Disruption Duration Estimator.
Uses empirical disruption historical duration matrices by event type and severity.
"""

DURATION_MATRIX: dict[tuple[str, str], tuple[int, int, int]] = {
    # (event_type, severity) -> (min_days, likely_days, max_days)
    ("weather", "critical"): (14, 21, 35),
    ("weather", "high"): (7, 14, 21),
    ("weather", "medium"): (3, 7, 10),
    ("weather", "low"): (1, 3, 5),

    ("geopolitical", "critical"): (30, 60, 120),
    ("geopolitical", "high"): (14, 30, 60),
    ("geopolitical", "medium"): (7, 14, 30),
    ("geopolitical", "low"): (3, 7, 14),

    ("port", "critical"): (10, 18, 30),
    ("port", "high"): (5, 12, 18),
    ("port", "medium"): (3, 6, 10),
    ("port", "low"): (1, 3, 5),

    ("supplier", "critical"): (14, 28, 60),
    ("supplier", "high"): (7, 16, 28),
    ("supplier", "medium"): (4, 8, 14),
    ("supplier", "low"): (2, 4, 7),

    ("transport", "critical"): (7, 14, 21),
    ("transport", "high"): (4, 8, 14),
    ("transport", "medium"): (2, 5, 8),
    ("transport", "low"): (1, 2, 4),
}


def estimate_disruption_days(event_type: str, severity: str) -> int:
    """
    Returns deterministic estimated disruption duration in days.
    """
    key = (event_type.lower(), severity.lower())
    if key in DURATION_MATRIX:
        return DURATION_MATRIX[key][1]  # Return the most likely days
    # Default fallback
    return 14
