"""
Supplier API endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models.supplier import Supplier, AlternateSupplier
from schemas.supplier import (
    SupplierOut,
    SupplierCreate,
    SupplierDetail,
    AlternateSupplierOut,
)

router = APIRouter(prefix="/api/suppliers", tags=["Suppliers"])


@router.get("", response_model=list[SupplierOut])
def list_suppliers(db: Session = Depends(get_db)):
    """List all suppliers."""
    return db.query(Supplier).all()


@router.get("/{supplier_id}", response_model=SupplierDetail)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Get supplier detail with BOM and inventory entries."""
    supplier = (
        db.query(Supplier)
        .options(
            joinedload(Supplier.bom_entries),
            joinedload(Supplier.inventory_entries),
        )
        .filter(Supplier.id == supplier_id)
        .first()
    )
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return supplier


@router.post("", response_model=SupplierOut, status_code=201)
def create_supplier(data: SupplierCreate, db: Session = Depends(get_db)):
    """Add a new supplier."""
    supplier = Supplier(**data.model_dump())
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


@router.get("/{supplier_id}/alternates", response_model=list[AlternateSupplierOut])
def get_alternates(supplier_id: int, db: Session = Depends(get_db)):
    """List alternate suppliers for a given primary supplier."""
    alts = (
        db.query(AlternateSupplier)
        .options(joinedload(AlternateSupplier.alternate_supplier))
        .filter(AlternateSupplier.primary_supplier_id == supplier_id)
        .order_by(AlternateSupplier.priority)
        .all()
    )
    return alts
