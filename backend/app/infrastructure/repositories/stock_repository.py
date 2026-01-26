"""
Repositorio para gestionar movimientos de stock.
"""

from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import StockMovement, Product, StockMovementType
from app.schemas.stock_movement import StockMovementCreate


class StockRepository:
    """
    Repositorio para operaciones relacionadas con movimientos de stock.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio de stock.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        self.db = db
    
    async def create_movement(
        self, 
        movement_in: StockMovementCreate, 
        current_stock: int
    ) -> StockMovement:
        """
        Crea un movimiento de stock y actualiza el stock del producto.
        
        Args:
            movement_in: Datos del movimiento a crear
            current_stock: Stock actual del producto
            
        Returns:
            Movimiento de stock creado
        """
        # Calcular el nuevo stock basándose en el tipo de movimiento
        if movement_in.movement_type == StockMovementType.ENTRADA:
            stock_after = current_stock + movement_in.quantity
        elif movement_in.movement_type == StockMovementType.SALIDA:
            stock_after = current_stock - movement_in.quantity
        else:  # AJUSTE
            stock_after = current_stock + movement_in.quantity
        
        # Crear la instancia de StockMovement
        db_movement = StockMovement(
            product_id=movement_in.product_id,
            movement_type=movement_in.movement_type,
            quantity=movement_in.quantity,
            stock_before=current_stock,
            stock_after=stock_after,
            reason=movement_in.reason,
            notes=movement_in.notes
        )
        
        # Agregar el movimiento a la base de datos
        self.db.add(db_movement)
        
        # Actualizar el stock_actual del producto
        stmt = (
            update(Product)
            .where(Product.id == movement_in.product_id)
            .values(stock_actual=stock_after)
        )
        await self.db.execute(stmt)
        
        # Hacer commit
        await self.db.commit()
        await self.db.refresh(db_movement)
        
        return db_movement
    
    async def get_movements_by_product(self, product_id: int) -> List[StockMovement]:
        """
        Obtiene el historial de movimientos de stock de un producto.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de movimientos ordenados por fecha de creación descendente
        """
        stmt = (
            select(StockMovement)
            .where(StockMovement.product_id == product_id)
            .order_by(StockMovement.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
