"""
Geographic Matcher.
Uses the Haversine formula to compute exact great-circle distance between
event impact coordinates and supplier physical facilities.
"""

import math
from typing import TypedDict


class GeoMatchResult(TypedDict):
    distance_km: float
    proximity_score: float
    is_in_range: bool


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes great-circle distance in kilometers between two points on Earth.
    """
    r = 6371.0  # Earth radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return r * c


def calculate_geo_proximity(
    event_lat: float | None,
    event_lon: float | None,
    event_radius_km: float,
    supplier_lat: float,
    supplier_lon: float,
    event_country: str | None = None,
    supplier_country: str | None = None,
) -> GeoMatchResult:
    """
    Calculates geographic proximity score (0.0 to 1.0).
    1.0 = Direct epicenter hit
    0.0 = Outside disruption radius
    """
    if event_lat is not None and event_lon is not None and (event_lat != 0.0 or event_lon != 0.0):
        distance = haversine_distance(event_lat, event_lon, supplier_lat, supplier_lon)
        effective_radius = max(event_radius_km, 100.0)

        if distance <= effective_radius:
            # Score scales linearly from 1.0 down to 0.1 at perimeter
            score = 1.0 - 0.9 * (distance / effective_radius)
            return {
                "distance_km": round(distance, 1),
                "proximity_score": round(max(0.1, min(1.0, score)), 3),
                "is_in_range": True,
            }

        # Check country match fallback within reasonable distance
        if event_country and supplier_country and event_country.lower() == supplier_country.lower():
            if distance <= effective_radius * 2.5:
                return {
                    "distance_km": round(distance, 1),
                    "proximity_score": 0.35,
                    "is_in_range": True,
                }

        return {
            "distance_km": round(distance, 1),
            "proximity_score": 0.0,
            "is_in_range": False,
        }

    # Fallback when event coordinates are missing: match country or region
    if event_country and supplier_country and event_country.lower() == supplier_country.lower():
        return {
            "distance_km": 50.0,
            "proximity_score": 0.75,
            "is_in_range": True,
        }

    return {
        "distance_km": 9999.0,
        "proximity_score": 0.0,
        "is_in_range": False,
    }
