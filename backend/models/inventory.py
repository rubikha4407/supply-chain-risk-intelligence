"""
Inventory model — tracks current stock of each component from each supplier.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
)
from sqlalchemy.orm import relationship

from database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    component_name = Column(String, nullable=False)
    current_stock = Column(Integer, nullable=False)         # units on hand
    daily_consumption = Column(Float, nullable=False)        # units per day
    last_updated = Column(
        DateTime, default=lambda: datetime.now(timezone.utc),
    )

    # Relationships
    product = relationship("Product", back_populates="inventory_entries")
    supplier = relationship("Supplier", back_populates="inventory_entries")

    @property
    def days_of_supply(self) -> float:
        """Deterministic calculation: current_stock / daily_consumption."""
        if self.daily_consumption <= 0:
            return float("inf")
        return round(self.current_stock / self.daily_consumption, 1)

    def __repr__(self):
        return (
            f"<Inventory {self.id}: {self.component_name}"
            f" — {self.current_stock} units ({self.days_of_supply}d)>"
        )
