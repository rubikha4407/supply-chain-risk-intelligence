"""
Deterministic Impact Engine.

Calculates:
1. Inventory runway (days until buffer depletion)
2. Exact stockout date (calendar projection)
3. Production impact percentage (capacity reduction)
4. Revenue and financial exposure (total $ value of halted finished goods)
"""

from datetime import datetime, timezone, timedelta
from typing import TypedDict
from sqlalchemy.orm import Session

from models.product import Product, BillOfMaterials
from models.inventory import Inventory
from models.supplier import Supplier


class ComponentImpact(TypedDict):
    product_id: int
    product_name: str
    product_sku: str
    component_name: str
    is_critical: bool
    current_stock: int
    daily_consumption: float
    inventory_runway_days: int
    stockout_date: datetime
    disruption_days: int
    shortage_days: int
    units_at_risk: int
    revenue_at_risk: float
    production_impact_pct: float
    impact_severity: str


class SupplierImpactSummary(TypedDict):
    supplier_id: int
    supplier_name: str
    disruption_days: int
    min_inventory_runway_days: int
    earliest_stockout_date: datetime | None
    total_units_at_risk: int
    total_revenue_at_risk: float
    highest_production_impact_pct: float
    impacted_products_count: int
    component_impacts: list[ComponentImpact]


class ImpactCalculator:
    """
    Deterministic BOM-traversing impact calculation engine.
    No statistical approximation — exact consumption arithmetic.
    """

    def calculate_supplier_impact(
        self,
        db: Session,
        supplier_id: int,
        disruption_days: int,
    ) -> SupplierImpactSummary:
        supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
        supplier_name = supplier.name if supplier else f"Supplier #{supplier_id}"

        # Fetch all BOM components sourced from this supplier
        boms = (
            db.query(BillOfMaterials)
            .filter(BillOfMaterials.supplier_id == supplier_id)
            .all()
        )

        component_impacts: list[ComponentImpact] = []
        now = datetime.now(timezone.utc)

        min_runway = 999
        earliest_stockout: datetime | None = None
        total_units = 0
        total_revenue = 0.0
        max_prod_impact = 0.0
        impacted_products = set()

        for bom in boms:
            product = db.query(Product).filter(Product.id == bom.product_id).first()
            if not product:
                continue

            # Find matching inventory record
            inv = (
                db.query(Inventory)
                .filter(
                    Inventory.supplier_id == supplier_id,
                    Inventory.component_name == bom.component_name,
                )
                .first()
            )

            current_stock = inv.current_stock if inv else 500
            daily_consumption = inv.daily_consumption if inv else float(product.daily_demand * bom.quantity_per_unit)
            if daily_consumption <= 0:
                daily_consumption = 10.0

            runway_days = int(current_stock / daily_consumption)
            stockout_dt = now + timedelta(days=runway_days)

            if runway_days < min_runway:
                min_runway = runway_days
                earliest_stockout = stockout_dt

            # Deterministic shortage arithmetic
            if disruption_days > runway_days:
                shortage_days = disruption_days - runway_days
                # Units of finished product delayed or halted
                units_risk = int(shortage_days * product.daily_demand)
                rev_risk = round(units_risk * product.unit_price, 2)

                if bom.is_critical:
                    # Critical component stops the entire product line
                    prod_impact = min(100.0, round((shortage_days / max(disruption_days, 1)) * 100.0, 1))
                else:
                    # Non-critical component causes line slowdown or delayed rework
                    prod_impact = min(50.0, round((shortage_days / max(disruption_days, 1)) * 40.0, 1))

                severity_tag = "CRITICAL" if prod_impact >= 75.0 else ("HIGH" if prod_impact >= 35.0 else "MEDIUM")
                impacted_products.add(product.id)
            else:
                # Buffer inventory is sufficient to absorb disruption
                shortage_days = 0
                units_risk = 0
                rev_risk = 0.0
                prod_impact = 0.0
                severity_tag = "LOW"

            total_units += units_risk
            total_revenue += rev_risk
            if prod_impact > max_prod_impact:
                max_prod_impact = prod_impact

            component_impacts.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_sku": product.sku,
                "component_name": bom.component_name,
                "is_critical": bom.is_critical,
                "current_stock": current_stock,
                "daily_consumption": daily_consumption,
                "inventory_runway_days": runway_days,
                "stockout_date": stockout_dt,
                "disruption_days": disruption_days,
                "shortage_days": shortage_days,
                "units_at_risk": units_risk,
                "revenue_at_risk": rev_risk,
                "production_impact_pct": prod_impact,
                "impact_severity": severity_tag,
            })

        if min_runway == 999:
            min_runway = 0

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "disruption_days": disruption_days,
            "min_inventory_runway_days": min_runway,
            "earliest_stockout_date": earliest_stockout,
            "total_units_at_risk": total_units,
            "total_revenue_at_risk": round(total_revenue, 2),
            "highest_production_impact_pct": max_prod_impact,
            "impacted_products_count": len(impacted_products),
            "component_impacts": component_impacts,
        }


impact_calculator = ImpactCalculator()
