import sys
from database import SessionLocal
from seed.seed_data import seed_database
from schemas.event import SimulateEventRequest
from routers.simulation import simulate_custom_event
import json

def test():
    db = SessionLocal()
    print("Seeding database if needed...")
    seed_database(db)
    db.close()

    db = SessionLocal()
    scenarios = [
        {
            "title": "Category 5 Typhoon hits Taiwan causing flooding and port closures.",
            "description": "Category 5 Typhoon hits Taiwan causing flooding and port closures."
        },
        {
            "title": "Suez Canal blockage causes major shipping delays.",
            "description": "Suez Canal blockage causes major shipping delays."
        },
        {
            "title": "Minor rainfall in a region far from all suppliers.",
            "description": "Minor rainfall in a region far from all suppliers."
        },
        {
            "title": "Supplier factory fire shuts down production.",
            "description": "Supplier factory fire shuts down production at Shenzhen MicroParts Ltd."
        }
    ]

    for i, sc in enumerate(scenarios, 1):
        print(f"\n--- SCENARIO {i}: {sc['title']} ---")
        req = SimulateEventRequest(title=sc['title'], description=sc['description'])
        result = simulate_custom_event(req, db)
        
        print("Event Type:", result["ai_understanding"]["event_type"])
        print("Severity:", result["ai_understanding"]["severity"])
        print("Assessments:", result["assessments_count"])
        
        for a in result["assessments"]:
            exp = a.get('ai_risk_explanation') or ""
            print(f"  Supplier ID: {a['supplier_id']}, Score: {a['risk_score']:.2f}, Level: {a['status']}")
            print(f"  Explanation: {exp[:100]}...")
            
    db.close()

if __name__ == "__main__":
    test()
