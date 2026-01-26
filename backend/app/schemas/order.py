"""
Esquemas Pydantic para órdenes.
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Optional
from pydantic import Field

from .base import MyBaseModel
from app.infrastructure.database.models import OrderStatus


class OrderItemCreate(MyBaseModel):
    """Esquema para crear un item de orden."""
    
    product_id: int
    quantity: int = Field(gt=0, description="Cantidad debe ser mayor a 0")


class OrderCreate(MyBaseModel):
    """Esquema para crear una orden."""
    
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
    shipping_postal_code: Optional[str] = None
    notes: Optional[str] = None


class OrderItemResponse(MyBaseModel):
    """Esquema de respuesta para un item de orden."""
    
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(MyBaseModel):
    """Esquema de respuesta para una orden."""
    
    id: int
    order_number: str
    status: OrderStatus
    total: Decimal
    created_at: datetime
    items: List[OrderItemResponse]
    shipping_address: Optional[str] = None
    shipping_city: Optional[str] = None
