"""
Esquemas Pydantic para productos.
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional

from .base import MyBaseModel


class ProductBase(MyBaseModel):
    """Esquema base para productos."""
    
    name: str
    description: Optional[str] = None
    price: Decimal
    category: str
    sku: str
    image_url: Optional[str] = None
    stock_minimo: int = 10


class ProductCreate(ProductBase):
    """Esquema para crear un producto."""
    
    stock_actual: int


class ProductUpdate(MyBaseModel):
    """Esquema para actualizar un producto."""
    
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    category: Optional[str] = None
    sku: Optional[str] = None
    image_url: Optional[str] = None
    stock_minimo: Optional[int] = None
    stock_actual: Optional[int] = None


class ProductResponse(ProductBase):
    """Esquema de respuesta para productos."""
    
    id: int
    created_at: datetime
    views_count: int
    ventas_count: int
    stock_actual: int
