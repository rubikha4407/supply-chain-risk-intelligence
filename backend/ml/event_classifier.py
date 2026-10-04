"""
AI/NLP Event Understanding Layer.

Performs:
1. Event type extraction (weather, geopolitical, port, supplier, transport)
2. Severity classification (low, medium, high, critical)
3. Location & coordinates extraction (country, region, lat/lng, radius)
4. Relevant entity extraction (ports, companies, infrastructure, materials)
5. Concise executive event summary generation
"""

import re
from typing import TypedDict


class ExtractedEntities(TypedDict):
    locations: list[str]
    organizations: list[str]
    facilities: list[str]
    components: list[str]


class EventUnderstandingResult(TypedDict):
    event_type: str
    severity: str
    affected_country: str | None
    affected_region: str | None
    latitude: float | None
    longitude: float | None
    radius_km: float
    entities: ExtractedEntities
    ai_summary: str


# Geographic coordinate reference for global supply chain hotspots
KNOWN_LOCATIONS: dict[str, dict] = {
    "taiwan": {"country": "Taiwan", "region": "East Asia", "lat": 24.7736, "lng": 120.9530, "radius": 350.0},
    "taipei": {"country": "Taiwan", "region": "East Asia", "lat": 25.0330, "lng": 121.5654, "radius": 200.0},
    "kaohsiung": {"country": "Taiwan", "region": "East Asia", "lat": 22.6273, "lng": 120.3014, "radius": 250.0},
    "hsinchu": {"country": "Taiwan", "region": "East Asia", "lat": 24.8039, "lng": 120.9647, "radius": 150.0},
    "south korea": {"country": "South Korea", "region": "East Asia", "lat": 37.2636, "lng": 127.0286, "radius": 300.0},
    "korea": {"country": "South Korea", "region": "East Asia", "lat": 37.2636, "lng": 127.0286, "radius": 300.0},
    "seoul": {"country": "South Korea", "region": "East Asia", "lat": 37.5665, "lng": 126.9780, "radius": 200.0},
    "suwon": {"country": "South Korea", "region": "East Asia", "lat": 37.2636, "lng": 127.0286, "radius": 150.0},
    "china": {"country": "China", "region": "East Asia", "lat": 22.5431, "lng": 114.0579, "radius": 500.0},
    "shenzhen": {"country": "China", "region": "East Asia", "lat": 22.5431, "lng": 114.0579, "radius": 200.0},
    "shanghai": {"country": "China", "region": "East Asia", "lat": 31.2304, "lng": 121.4737, "radius": 300.0},
    "ningbo": {"country": "China", "region": "East Asia", "lat": 29.8683, "lng": 121.5440, "radius": 250.0},
    "japan": {"country": "Japan", "region": "East Asia", "lat": 35.6762, "lng": 139.6503, "radius": 400.0},
    "tokyo": {"country": "Japan", "region": "East Asia", "lat": 35.6762, "lng": 139.6503, "radius": 200.0},
    "yokohama": {"country": "Japan", "region": "East Asia", "lat": 35.4437, "lng": 139.6380, "radius": 200.0},
    "germany": {"country": "Germany", "region": "Europe", "lat": 48.1351, "lng": 11.5820, "radius": 400.0},
    "munich": {"country": "Germany", "region": "Europe", "lat": 48.1351, "lng": 11.5820, "radius": 200.0},
    "bavaria": {"country": "Germany", "region": "Europe", "lat": 48.7904, "lng": 11.4979, "radius": 250.0},
    "mexico": {"country": "Mexico", "region": "North America", "lat": 25.6866, "lng": -100.3161, "radius": 400.0},
    "monterrey": {"country": "Mexico", "region": "North America", "lat": 25.6866, "lng": -100.3161, "radius": 200.0},
    "india": {"country": "India", "region": "South Asia", "lat": 23.0225, "lng": 72.5714, "radius": 500.0},
    "gujarat": {"country": "India", "region": "South Asia", "lat": 23.0225, "lng": 72.5714, "radius": 300.0},
    "ahmedabad": {"country": "India", "region": "South Asia", "lat": 23.0225, "lng": 72.5714, "radius": 200.0},
    "united states": {"country": "United States", "region": "North America", "lat": 45.5152, "lng": -122.6784, "radius": 500.0},
    "oregon": {"country": "United States", "region": "North America", "lat": 45.5152, "lng": -122.6784, "radius": 300.0},
    "portland": {"country": "United States", "region": "North America", "lat": 45.5152, "lng": -122.6784, "radius": 200.0},
    "suez": {"country": "Egypt", "region": "Middle East", "lat": 30.4570, "lng": 32.3510, "radius": 5000.0},
    "red sea": {"country": "Yemen/Egypt", "region": "Middle East", "lat": 20.0000, "lng": 38.0000, "radius": 5000.0},
    "panama": {"country": "Panama", "region": "Central America", "lat": 9.1012, "lng": -79.6955, "radius": 5000.0},
    "rotterdam": {"country": "Netherlands", "region": "Europe", "lat": 51.9244, "lng": 4.4777, "radius": 250.0},
    "singapore": {"country": "Singapore", "region": "Southeast Asia", "lat": 1.3521, "lng": 103.8198, "radius": 200.0},
}

TYPE_KEYWORDS: dict[str, list[str]] = {
    "weather": [
        "typhoon", "hurricane", "cyclone", "flood", "flooding", "earthquake",
        "storm", "tsunami", "monsoon", "tornado", "heavy rain", "gale",
    ],
    "port": [
        "port", "dock", "terminal", "container", "berth", "congestion",
        "anchorage", "cargo backlog", "demurrage", "harbor", "quay",
    ],
    "geopolitical": [
        "sanctions", "tariff", "embargo", "export control", "trade war",
        "geopolitical", "military", "blockade", "protest", "strike", "conflict",
    ],
    "supplier": [
        "factory fire", "plant fire", "fab shutdown", "explosion", "equipment failure",
        "bankruptcy", "insolvency", "quality recall", "worker strike", "production halt",
        "contamination", "cleanroom",
    ],
    "transport": [
        "canal blocked", "blockage", "grounding", "vessel", "shipment delay", "shipping delays", "freight disruption",
        "rail strike", "airspace closure", "pipeline leak", "carrier", "logistics route",
    ],
}

SEVERITY_KEYWORDS: dict[str, list[str]] = {
    "critical": [
        "catastrophic", "devastating", "complete shutdown", "force majeure",
        "category 5", "category 4", "massive", "emergency", "fatal", "unprecedented",
        "halted completely", "blocked completely", "crippling",
    ],
    "high": [
        "severe", "major", "significant", "widespread", "extensive", "category 3",
        "shut down", "halted", "suspended", "closure", "heavy damage", "indefinitely",
    ],
    "medium": [
        "moderate", "partial", "temporary", "delays expected", "intermittent",
        "constrained", "slowdown", "backlog", "category 2", "warning",
    ],
    "low": [
        "minor", "potential", "advisory", "monitoring", "slight", "minimal",
        "category 1", "localized", "brief",
    ],
}

KNOWN_ORGANIZATIONS = [
    "TSMC", "Taiwan Semiconductor", "Samsung", "Samsung Electronics",
    "Tokyo Precision", "Bayern Semiconductor", "Shenzhen MicroParts",
    "Monterrey Electronics", "Gujarat Circuit Systems", "Portland Connectors",
    "Evergreen", "Maersk", "MSC", "Cosco", "Foxconn",
]

KNOWN_FACILITIES = [
    "Port of Kaohsiung", "Port of Taipei", "Hsinchu Science Park",
    "Port of Shenzhen", "Port of Shanghai", "Port of Rotterdam",
    "Port of Los Angeles", "Suez Canal", "Panama Canal", "Strait of Malacca",
    "Fab 18", "Fab 2", "Semiconductor Cleanroom",
]

KNOWN_COMPONENTS = [
    "MCU-7nm-A1", "OLED-Display-3.5", "PCB-4Layer-SM", "USB-C-Connector",
    "PowerMOS-FET-60V", "DSP-Chip-28nm", "DRAM-4GB-Module", "Heatsink-AL-40mm",
    "MEMS-Accel-3Axis", "Flex-Cable-200mm", "BLE-Module-5.0", "WiFi-SoC-6E",
    "microchip", "semiconductor", "wafer", "sensor", "display", "capacitor",
]


class EventClassifier:
    """
    AI/NLP Event Understanding Layer.
    Extracts structured domain signals, entities, and summaries from free-text reports.
    """

    def understand_event(self, title: str, description: str) -> EventUnderstandingResult:
        full_text = f"{title} {description}".lower()

        # 1. Event Type Extraction
        event_type = self._extract_event_type(full_text)

        # 2. Severity Classification
        severity = self._extract_severity(full_text)

        # 3. Location Extraction & Geo-reference resolution
        loc_data = self._extract_location(full_text)

        # 4. Entity Extraction (Locations, Organizations, Facilities, Components)
        entities = self._extract_entities(f"{title} {description}")

        # 5. Executive AI Summary Generation
        ai_summary = self._generate_summary(title, description, event_type, severity, loc_data)

        return {
            "event_type": event_type,
            "severity": severity,
            "affected_country": loc_data.get("country"),
            "affected_region": loc_data.get("region"),
            "latitude": loc_data.get("lat"),
            "longitude": loc_data.get("lng"),
            "radius_km": loc_data.get("radius", 200.0),
            "entities": entities,
            "ai_summary": ai_summary,
        }

    def _extract_event_type(self, text: str) -> str:
        scores = {etype: 0 for etype in TYPE_KEYWORDS}
        for etype, keywords in TYPE_KEYWORDS.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", text):
                    scores[etype] += 2 if len(kw.split()) > 1 else 1

        best_type = max(scores, key=scores.get)
        return best_type if scores[best_type] > 0 else "weather"

    def _extract_severity(self, text: str) -> str:
        for sev, keywords in SEVERITY_KEYWORDS.items():
            for kw in keywords:
                if re.search(rf"\b{re.escape(kw)}\b", text):
                    return sev
        return "medium"

    def _extract_location(self, text: str) -> dict:
        for key, loc in KNOWN_LOCATIONS.items():
            if re.search(rf"\b{re.escape(key)}\b", text):
                return loc
        return {
            "country": "Unknown",
            "region": "Global",
            "lat": 0.0,
            "lng": 0.0,
            "radius": 250.0,
        }

    def _extract_entities(self, text: str) -> ExtractedEntities:
        locations_found = []
        for key in KNOWN_LOCATIONS:
            if re.search(rf"\b{re.escape(key)}\b", text, flags=re.IGNORECASE):
                locations_found.append(key.title())

        orgs_found = [
            org for org in KNOWN_ORGANIZATIONS
            if re.search(rf"\b{re.escape(org)}\b", text, flags=re.IGNORECASE)
        ]

        facilities_found = [
            fac for fac in KNOWN_FACILITIES
            if re.search(rf"\b{re.escape(fac)}\b", text, flags=re.IGNORECASE)
        ]

        components_found = [
            comp for comp in KNOWN_COMPONENTS
            if re.search(rf"\b{re.escape(comp)}\b", text, flags=re.IGNORECASE)
        ]

        return {
            "locations": list(dict.fromkeys(locations_found)),
            "organizations": list(dict.fromkeys(orgs_found)),
            "facilities": list(dict.fromkeys(facilities_found)),
            "components": list(dict.fromkeys(components_found)),
        }

    def _generate_summary(
        self,
        title: str,
        description: str,
        event_type: str,
        severity: str,
        loc_data: dict,
    ) -> str:
        loc_str = loc_data.get("country") or loc_data.get("region") or "an active trade corridor"
        return (
            f"AI Signal Detection: {severity.upper()} {event_type} event affecting {loc_str}. "
            f"Primary disruption vector: {title.strip()}. "
            f"Supply chain vulnerability flagged within {int(loc_data.get('radius', 200))}km impact zone. "
            f"Immediate inventory burndown and alternate sourcing protocol required."
        )


event_classifier = EventClassifier()
