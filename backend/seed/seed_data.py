"""
Seed the database with realistic demo data for the supply chain scenario.

Scenario overview:
  - An electronics company (OEM) that manufactures consumer products
  - 8 suppliers across Asia, Europe, and North America
  - 4 products (SmartWidget Pro, PowerBoard X, SensorArray Elite, ConnectHub Mini)
  - BOM linking components to suppliers
  - Inventory with realistic stock levels and consumption rates
  - Alternate suppliers for critical components
"""

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from models.supplier import Supplier, AlternateSupplier
from models.product import Product, BillOfMaterials
from models.inventory import Inventory


def seed_database(db: Session) -> None:
    """Populate the database with demo data. Skips if data already exists."""

    if db.query(Supplier).count() > 0:
        print("  ⏭️  Database already seeded. Skipping.")
        return

    print("  🌱 Seeding suppliers...")
    suppliers = _seed_suppliers(db)

    print("  🌱 Seeding products...")
    products = _seed_products(db)

    print("  🌱 Seeding bill of materials...")
    _seed_bom(db, suppliers, products)

    print("  🌱 Seeding inventory...")
    _seed_inventory(db, suppliers, products)

    print("  🌱 Seeding alternate suppliers...")
    _seed_alternates(db, suppliers)

    db.commit()
    print("  ✅ Seed data loaded successfully!")


def _seed_suppliers(db: Session) -> dict[str, Supplier]:
    """Create 8 realistic suppliers."""
    data = [
        {
            "name": "Taiwan Semiconductor Manufacturing",
            "country": "Taiwan",
            "region": "East Asia",
            "latitude": 24.7736,
            "longitude": 120.9530,
            "tier": "Tier 1",
            "reliability_score": 0.95,
        },
        {
            "name": "Samsung Electronics Components",
            "country": "South Korea",
            "region": "East Asia",
            "latitude": 37.2636,
            "longitude": 127.0286,
            "tier": "Tier 1",
            "reliability_score": 0.93,
        },
        {
            "name": "Shenzhen MicroParts Ltd",
            "country": "China",
            "region": "East Asia",
            "latitude": 22.5431,
            "longitude": 114.0579,
            "tier": "Tier 2",
            "reliability_score": 0.85,
        },
        {
            "name": "Tokyo Precision Electronics",
            "country": "Japan",
            "region": "East Asia",
            "latitude": 35.6762,
            "longitude": 139.6503,
            "tier": "Tier 1",
            "reliability_score": 0.97,
        },
        {
            "name": "Bayern Semiconductor GmbH",
            "country": "Germany",
            "region": "Europe",
            "latitude": 48.1351,
            "longitude": 11.5820,
            "tier": "Tier 1",
            "reliability_score": 0.96,
        },
        {
            "name": "Monterrey Electronics SA",
            "country": "Mexico",
            "region": "North America",
            "latitude": 25.6866,
            "longitude": -100.3161,
            "tier": "Tier 2",
            "reliability_score": 0.88,
        },
        {
            "name": "Gujarat Circuit Systems",
            "country": "India",
            "region": "South Asia",
            "latitude": 23.0225,
            "longitude": 72.5714,
            "tier": "Tier 2",
            "reliability_score": 0.82,
        },
        {
            "name": "Portland Connectors Inc",
            "country": "United States",
            "region": "North America",
            "latitude": 45.5152,
            "longitude": -122.6784,
            "tier": "Tier 1",
            "reliability_score": 0.91,
        },
    ]

    suppliers = {}
    for item in data:
        s = Supplier(**item)
        db.add(s)
        db.flush()
        suppliers[s.name] = s

    return suppliers


def _seed_products(db: Session) -> dict[str, Product]:
    """Create 4 products."""
    data = [
        {
            "name": "SmartWidget Pro",
            "sku": "SWP-001",
            "category": "Consumer Electronics",
            "unit_price": 149.99,
            "daily_demand": 100,
        },
        {
            "name": "PowerBoard X",
            "sku": "PBX-002",
            "category": "Industrial Controllers",
            "unit_price": 299.99,
            "daily_demand": 50,
        },
        {
            "name": "SensorArray Elite",
            "sku": "SAE-003",
            "category": "IoT Sensors",
            "unit_price": 79.99,
            "daily_demand": 200,
        },
        {
            "name": "ConnectHub Mini",
            "sku": "CHM-004",
            "category": "Networking",
            "unit_price": 199.99,
            "daily_demand": 75,
        },
    ]

    products = {}
    for item in data:
        p = Product(**item)
        db.add(p)
        db.flush()
        products[p.name] = p

    return products


def _seed_bom(
    db: Session,
    suppliers: dict[str, Supplier],
    products: dict[str, Product],
) -> None:
    """Create BOM entries linking products → components → suppliers."""

    tsmc = suppliers["Taiwan Semiconductor Manufacturing"]
    samsung = suppliers["Samsung Electronics Components"]
    shenzhen = suppliers["Shenzhen MicroParts Ltd"]
    tokyo = suppliers["Tokyo Precision Electronics"]
    bayern = suppliers["Bayern Semiconductor GmbH"]
    monterrey = suppliers["Monterrey Electronics SA"]
    gujarat = suppliers["Gujarat Circuit Systems"]
    portland = suppliers["Portland Connectors Inc"]

    swp = products["SmartWidget Pro"]
    pbx = products["PowerBoard X"]
    sae = products["SensorArray Elite"]
    chm = products["ConnectHub Mini"]

    bom_data = [
        # SmartWidget Pro — depends on Taiwan + Japan + China
        {"product_id": swp.id, "supplier_id": tsmc.id, "component_name": "MCU-7nm-A1", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 14},
        {"product_id": swp.id, "supplier_id": tokyo.id, "component_name": "OLED-Display-3.5", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 10},
        {"product_id": swp.id, "supplier_id": shenzhen.id, "component_name": "PCB-4Layer-SM", "quantity_per_unit": 1, "is_critical": False, "lead_time_days": 7},
        {"product_id": swp.id, "supplier_id": portland.id, "component_name": "USB-C-Connector", "quantity_per_unit": 2, "is_critical": False, "lead_time_days": 5},

        # PowerBoard X — depends on Germany + Taiwan + Korea
        {"product_id": pbx.id, "supplier_id": bayern.id, "component_name": "PowerMOS-FET-60V", "quantity_per_unit": 4, "is_critical": True, "lead_time_days": 12},
        {"product_id": pbx.id, "supplier_id": tsmc.id, "component_name": "DSP-Chip-28nm", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 14},
        {"product_id": pbx.id, "supplier_id": samsung.id, "component_name": "DRAM-4GB-Module", "quantity_per_unit": 2, "is_critical": False, "lead_time_days": 8},
        {"product_id": pbx.id, "supplier_id": monterrey.id, "component_name": "Heatsink-AL-40mm", "quantity_per_unit": 1, "is_critical": False, "lead_time_days": 6},

        # SensorArray Elite — depends on Japan + India + Korea
        {"product_id": sae.id, "supplier_id": tokyo.id, "component_name": "MEMS-Accel-3Axis", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 10},
        {"product_id": sae.id, "supplier_id": gujarat.id, "component_name": "Flex-Cable-200mm", "quantity_per_unit": 3, "is_critical": False, "lead_time_days": 5},
        {"product_id": sae.id, "supplier_id": samsung.id, "component_name": "BLE-Module-5.0", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 9},

        # ConnectHub Mini — depends on Taiwan + US + China
        {"product_id": chm.id, "supplier_id": tsmc.id, "component_name": "WiFi-SoC-6E", "quantity_per_unit": 1, "is_critical": True, "lead_time_days": 14},
        {"product_id": chm.id, "supplier_id": portland.id, "component_name": "RJ45-Jack-Shielded", "quantity_per_unit": 4, "is_critical": False, "lead_time_days": 4},
        {"product_id": chm.id, "supplier_id": shenzhen.id, "component_name": "Enclosure-ABS-Compact", "quantity_per_unit": 1, "is_critical": False, "lead_time_days": 7},
    ]

    for entry in bom_data:
        db.add(BillOfMaterials(**entry))


def _seed_inventory(
    db: Session,
    suppliers: dict[str, Supplier],
    products: dict[str, Product],
) -> None:
    """Create inventory entries with varying stock levels to make the demo interesting."""

    tsmc = suppliers["Taiwan Semiconductor Manufacturing"]
    samsung = suppliers["Samsung Electronics Components"]
    shenzhen = suppliers["Shenzhen MicroParts Ltd"]
    tokyo = suppliers["Tokyo Precision Electronics"]
    bayern = suppliers["Bayern Semiconductor GmbH"]
    monterrey = suppliers["Monterrey Electronics SA"]
    gujarat = suppliers["Gujarat Circuit Systems"]
    portland = suppliers["Portland Connectors Inc"]

    swp = products["SmartWidget Pro"]
    pbx = products["PowerBoard X"]
    sae = products["SensorArray Elite"]
    chm = products["ConnectHub Mini"]

    inventory_data = [
        # SmartWidget Pro components — Taiwan chip is LOW STOCK (8 days)
        {"product_id": swp.id, "supplier_id": tsmc.id, "component_name": "MCU-7nm-A1", "current_stock": 800, "daily_consumption": 100},
        {"product_id": swp.id, "supplier_id": tokyo.id, "component_name": "OLED-Display-3.5", "current_stock": 2000, "daily_consumption": 100},
        {"product_id": swp.id, "supplier_id": shenzhen.id, "component_name": "PCB-4Layer-SM", "current_stock": 3000, "daily_consumption": 100},
        {"product_id": swp.id, "supplier_id": portland.id, "component_name": "USB-C-Connector", "current_stock": 5000, "daily_consumption": 200},

        # PowerBoard X components
        {"product_id": pbx.id, "supplier_id": bayern.id, "component_name": "PowerMOS-FET-60V", "current_stock": 1200, "daily_consumption": 200},
        {"product_id": pbx.id, "supplier_id": tsmc.id, "component_name": "DSP-Chip-28nm", "current_stock": 500, "daily_consumption": 50},
        {"product_id": pbx.id, "supplier_id": samsung.id, "component_name": "DRAM-4GB-Module", "current_stock": 1500, "daily_consumption": 100},
        {"product_id": pbx.id, "supplier_id": monterrey.id, "component_name": "Heatsink-AL-40mm", "current_stock": 2500, "daily_consumption": 50},

        # SensorArray Elite components — Japan MEMS sensor is MEDIUM STOCK
        {"product_id": sae.id, "supplier_id": tokyo.id, "component_name": "MEMS-Accel-3Axis", "current_stock": 2400, "daily_consumption": 200},
        {"product_id": sae.id, "supplier_id": gujarat.id, "component_name": "Flex-Cable-200mm", "current_stock": 9000, "daily_consumption": 600},
        {"product_id": sae.id, "supplier_id": samsung.id, "component_name": "BLE-Module-5.0", "current_stock": 3000, "daily_consumption": 200},

        # ConnectHub Mini components — Taiwan WiFi chip is LOW STOCK
        {"product_id": chm.id, "supplier_id": tsmc.id, "component_name": "WiFi-SoC-6E", "current_stock": 600, "daily_consumption": 75},
        {"product_id": chm.id, "supplier_id": portland.id, "component_name": "RJ45-Jack-Shielded", "current_stock": 6000, "daily_consumption": 300},
        {"product_id": chm.id, "supplier_id": shenzhen.id, "component_name": "Enclosure-ABS-Compact", "current_stock": 3750, "daily_consumption": 75},
    ]

    for entry in inventory_data:
        db.add(Inventory(**entry))


def _seed_alternates(db: Session, suppliers: dict[str, Supplier]) -> None:
    """Create alternate supplier mappings for critical components."""

    tsmc = suppliers["Taiwan Semiconductor Manufacturing"]
    samsung = suppliers["Samsung Electronics Components"]
    tokyo = suppliers["Tokyo Precision Electronics"]
    bayern = suppliers["Bayern Semiconductor GmbH"]
    gujarat = suppliers["Gujarat Circuit Systems"]

    alternates_data = [
        # Samsung can substitute for TSMC chips (higher cost, longer lead time)
        {
            "primary_supplier_id": tsmc.id,
            "alternate_supplier_id": samsung.id,
            "component_name": "MCU-7nm-A1",
            "cost_multiplier": 1.25,
            "lead_time_days": 21,
            "priority": 1,
        },
        {
            "primary_supplier_id": tsmc.id,
            "alternate_supplier_id": bayern.id,
            "component_name": "DSP-Chip-28nm",
            "cost_multiplier": 1.40,
            "lead_time_days": 18,
            "priority": 1,
        },
        # Gujarat can substitute for Tokyo sensors
        {
            "primary_supplier_id": tokyo.id,
            "alternate_supplier_id": gujarat.id,
            "component_name": "MEMS-Accel-3Axis",
            "cost_multiplier": 1.15,
            "lead_time_days": 14,
            "priority": 1,
        },
        # Samsung is backup for TSMC WiFi chips
        {
            "primary_supplier_id": tsmc.id,
            "alternate_supplier_id": samsung.id,
            "component_name": "WiFi-SoC-6E",
            "cost_multiplier": 1.30,
            "lead_time_days": 20,
            "priority": 1,
        },
    ]

    for entry in alternates_data:
        db.add(AlternateSupplier(**entry))
