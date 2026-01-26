"""
Endpoints para operaciones relacionadas con movimientos de stock.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.stock_movement import StockMovementCreate, StockMovementResponse
from app.application.services.stock_service import StockService
from app.infrastructure.api.v1.deps import get_stock_service, get_current_admin
from app.infrastructure.database.models import User


router = APIRouter()


@router.post(
    "/",
    response_model=StockMovementResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar movimiento de stock (Solo admins)"
)
async def register_movement(
    movement_in: StockMovementCreate,
    service: Annotated[StockService, Depends(get_stock_service)],
    current_admin: Annotated[User, Depends(get_current_admin)]
) -> StockMovementResponse:
    """
    Registra un nuevo movimiento de stock. Solo accesible por administradores.
    
    Args:
        movement_in: Datos del movimiento a registrar
        service: Servicio de stock
        current_admin: Usuario administrador autenticado
        
    Returns:
        Movimiento de stock creado
        
    Raises:
        HTTPException: Si el producto no existe (404) o stock insuficiente (400)
    """
    try:
        movement = await service.register_movement(movement_in)
        return movement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(e)
        )


@router.get(
    "/product/{product_id}",
    response_model=List[StockMovementResponse],
    summary="Ver historial de movimientos de un producto"
)
async def get_product_movements(
    product_id: int,
    service: Annotated[StockService, Depends(get_stock_service)]
) -> List[StockMovementResponse]:
    """
    Obtiene el historial de movimientos de stock de un producto específico.
    
    Args:
        product_id: ID del producto
        service: Servicio de stock
        
    Returns:
        Lista de movimientos de stock ordenados por fecha descendente
        
    Raises:
        HTTPException: Si el producto no existe (404)
    """
    movements = await service.get_product_movements(product_id)
    return movements
