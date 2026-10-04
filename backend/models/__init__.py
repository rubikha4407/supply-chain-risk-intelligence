"""
SQLAlchemy ORM models.

Import all models here so that Base.metadata.create_all() discovers every table.
"""

from models.supplier import Supplier, AlternateSupplier  # noqa: F401
from models.product import Product, BillOfMaterials       # noqa: F401
from models.inventory import Inventory                     # noqa: F401
from models.event import ExternalEvent                     # noqa: F401
from models.recovery import (                              # noqa: F401
    RiskAssessment,
    ImpactAnalysis,
    RecoveryPlan,
    RecoveryAction,
)
