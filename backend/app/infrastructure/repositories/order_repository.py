"""
Repositorio para gestionar operaciones CRUD de órdenes.
"""

from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.infrastructure.database.repository import BaseRepository
from app.infrastructure.database.models import Order, OrderItem
from app.schemas.order import OrderCreate, OrderResponse


class OrderRepository(BaseRepository[Order, OrderCreate, OrderResponse]):
    """
    Repositorio para operaciones relacionadas con órdenes.
    
    Hereda de BaseRepository proporcionando todas las operaciones CRUD básicas
    para el modelo Order, además de métodos especializados para órdenes.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio de órdenes.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(Order, db)
    
    async def get_by_user(self, user_id: int) -> List[Order]:
        """
        Obtiene todas las órdenes de un usuario específico.
        
        Carga eager de los items de la orden y los productos asociados
        para evitar el problema N+1 queries.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de órdenes del usuario con items y productos cargados
        """
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
            .order_by(Order.created_at.desc())
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
