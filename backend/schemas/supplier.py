"""
Pydantic schemas for Supplier-related request/response models.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Supplier
# ---------------------------------------------------------------------------
class SupplierBase(BaseModel):
    name: str
    country: str
    region: str
    latitude: float
    longitude: float
    tier: str = "Tier 1"
    reliability_score: float = 0.9
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class SupplierDetail(SupplierOut):
    """Extended supplier view with nested BOM, inventory, and risk info."""
    bom_entries: list["BOMOut"] = []
    inventory_entries: list["InventoryOut"] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# BillOfMaterials
# ---------------------------------------------------------------------------
class BOMOut(BaseModel):
    id: int
    product_id: int
    supplier_id: int
    component_name: str
    quantity_per_unit: int
    is_critical: bool
    lead_time_days: float

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Inventory
# ---------------------------------------------------------------------------
class InventoryOut(BaseModel):
    id: int
    product_id: int
    supplier_id: int
    component_name: str
    current_stock: int
    daily_consumption: float
    days_of_supply: float
    last_updated: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# AlternateSupplier
# ---------------------------------------------------------------------------
class AlternateSupplierOut(BaseModel):
    id: int
    primary_supplier_id: int
    alternate_supplier_id: int
    component_name: str
    cost_multiplier: float
    lead_time_days: float
    priority: int
    alternate_supplier: Optional[SupplierOut] = None

    model_config = {"from_attributes": True}


# Rebuild models to resolve forward references
SupplierDetail.model_rebuild()
