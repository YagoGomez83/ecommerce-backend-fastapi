"""
Servicio de stock que implementa la lógica de negocio.
"""

from typing import List

from fastapi import HTTPException, status

from app.infrastructure.repositories.stock_repository import StockRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.database.models import StockMovement, StockMovementType
from app.schemas.stock_movement import StockMovementCreate


class StockService:
    """
    Servicio que gestiona la lógica de negocio relacionada con movimientos de stock.
    
    Actúa como intermediario entre la API y el repositorio, implementando
    validaciones y reglas de negocio específicas.
    """
    
    def __init__(
        self, 
        stock_repository: StockRepository,
        product_repository: ProductRepository
    ):
        """
        Inicializa el servicio de stock.
        
        Args:
            stock_repository: Repositorio de stock para operaciones de datos
            product_repository: Repositorio de productos para consultas
        """
        self.stock_repo = stock_repository
        self.product_repo = product_repository
    
    async def register_movement(self, movement_in: StockMovementCreate) -> StockMovement:
        """
        Registra un movimiento de stock.
        
        Args:
            movement_in: Datos del movimiento a registrar
            
        Returns:
            Movimiento de stock creado
            
        Raises:
            HTTPException: Si el producto no existe (404)
            ValueError: Si el stock es insuficiente para una salida
        """
        # Obtener el producto
        product = await self.product_repo.get_by_id(movement_in.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {movement_in.product_id} no encontrado"
            )
        
        # Verificar stock suficiente si es una salida
        if movement_in.movement_type == StockMovementType.SALIDA:
            if product.stock_actual < movement_in.quantity:
                raise ValueError(
                    f"Stock insuficiente. Stock actual: {product.stock_actual}, "
                    f"cantidad solicitada: {movement_in.quantity}"
                )
        
        # Crear el movimiento
        movement = await self.stock_repo.create_movement(
            movement_in=movement_in,
            current_stock=product.stock_actual
        )
        
        return movement
    
    async def get_product_movements(self, product_id: int) -> List[StockMovement]:
        """
        Obtiene el historial de movimientos de stock de un producto.
        
        Args:
            product_id: ID del producto
            
        Returns:
            Lista de movimientos de stock
            
        Raises:
            HTTPException: Si el producto no existe (404)
        """
        # Verificar que el producto existe
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Producto con ID {product_id} no encontrado"
            )
        
        # Obtener los movimientos
        movements = await self.stock_repo.get_movements_by_product(product_id)
        return movements
