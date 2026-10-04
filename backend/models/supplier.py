"""
Supplier and AlternateSupplier models.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    country = Column(String, nullable=False)
    region = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    tier = Column(String, default="Tier 1")  # Tier 1 / Tier 2
    reliability_score = Column(Float, default=0.9)  # 0.0 – 1.0
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    bom_entries = relationship("BillOfMaterials", back_populates="supplier")
    inventory_entries = relationship("Inventory", back_populates="supplier")
    risk_assessments = relationship("RiskAssessment", back_populates="supplier")
    primary_alternates = relationship(
        "AlternateSupplier",
        foreign_keys="AlternateSupplier.primary_supplier_id",
        back_populates="primary_supplier",
    )

    def __repr__(self):
        return f"<Supplier {self.id}: {self.name} ({self.country})>"


class AlternateSupplier(Base):
    __tablename__ = "alternate_suppliers"

    id = Column(Integer, primary_key=True, index=True)
    primary_supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    alternate_supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    component_name = Column(String, nullable=False)
    cost_multiplier = Column(Float, default=1.0)
    lead_time_days = Column(Float, default=7.0)
    priority = Column(Integer, default=1)  # 1 = first choice

    # Relationships
    primary_supplier = relationship(
        "Supplier",
        foreign_keys=[primary_supplier_id],
        back_populates="primary_alternates",
    )
    alternate_supplier = relationship(
        "Supplier",
        foreign_keys=[alternate_supplier_id],
    )

    def __repr__(self):
        return (
            f"<AlternateSupplier {self.primary_supplier_id}"
            f" -> {self.alternate_supplier_id} ({self.component_name})>"
        )
