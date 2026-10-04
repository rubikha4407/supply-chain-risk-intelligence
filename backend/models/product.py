"""
Product and BillOfMaterials (BOM) models.
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    unit_price = Column(Float, nullable=False)
    daily_demand = Column(Float, nullable=False)  # units per day

    # Relationships
    bom_entries = relationship("BillOfMaterials", back_populates="product")
    inventory_entries = relationship("Inventory", back_populates="product")
    impact_analyses = relationship("ImpactAnalysis", back_populates="product")

    def __repr__(self):
        return f"<Product {self.id}: {self.name} ({self.sku})>"


class BillOfMaterials(Base):
    __tablename__ = "bill_of_materials"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    component_name = Column(String, nullable=False)
    quantity_per_unit = Column(Integer, default=1)
    is_critical = Column(Boolean, default=False)
    lead_time_days = Column(Float, default=7.0)

    # Relationships
    product = relationship("Product", back_populates="bom_entries")
    supplier = relationship("Supplier", back_populates="bom_entries")

    def __repr__(self):
        return f"<BOM {self.id}: {self.component_name} for Product {self.product_id}>"
