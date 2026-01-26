"""
Esquemas Pydantic para movimientos de stock.
"""

from datetime import datetime
from typing import Optional
from pydantic import Field

from .base import MyBaseModel
from app.infrastructure.database.models import StockMovementType


class StockMovementBase(MyBaseModel):
    """Esquema base para movimientos de stock."""
    
    movement_type: StockMovementType
    quantity: int = Field(gt=0)
    reason: Optional[str] = None
    notes: Optional[str] = None


class StockMovementCreate(StockMovementBase):
    """Esquema para crear un movimiento de stock."""
    
    product_id: int


class StockMovementResponse(StockMovementBase):
    """Esquema de respuesta para movimientos de stock."""
    
    id: int
    stock_before: int
    stock_after: int
    created_at: datetime
