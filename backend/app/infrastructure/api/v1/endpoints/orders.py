"""
Endpoints para operaciones relacionadas con órdenes.
"""

from typing import Annotated, List
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.order import OrderCreate, OrderResponse, OrderItemResponse, OrderUpdateStatus
from app.application.services.order_service import OrderService
from app.infrastructure.api.v1.deps import get_order_service, get_current_user, get_current_admin
from app.infrastructure.database.models import User


router = APIRouter()


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear orden"
)
async def create_order(
    order_in: OrderCreate,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> OrderResponse:
    """
    Crea una nueva orden. Cualquier usuario autenticado puede realizar una compra.
    
    El backend calcula automáticamente:
    - Precios unitarios desde la base de datos
    - Subtotales de cada item
    - Total de la orden
    - Validación de stock disponible
    - Registro de movimientos de stock
    
    Args:
        order_in: Datos de la orden (items con product_id y cantidad)
        service: Servicio de órdenes
        current_user: Usuario autenticado
        
    Returns:
        Orden creada con todos los detalles calculados
        
    Raises:
        HTTPException: Si un producto no existe (404) o hay stock insuficiente (400)
    """
    try:
        order = await service.create_order(current_user.id, order_in)
        
        # Convertir a OrderResponse
        items_response = [
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal))
            )
            for item in order.order_items
        ]
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total=Decimal(str(order.total)),
            created_at=order.created_at,
            items=items_response,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city
        )
    except HTTPException:
        # Re-lanzar excepciones HTTP tal cual
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la orden: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[OrderResponse],
    summary="Obtener mis órdenes"
)
async def get_my_orders(
    service: Annotated[OrderService, Depends(get_order_service)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> List[OrderResponse]:
    """
    Obtiene todas las órdenes del usuario autenticado.
    
    Retorna las órdenes ordenadas por fecha de creación (más recientes primero),
    con todos los items y detalles de productos cargados.
    
    Args:
        service: Servicio de órdenes
        current_user: Usuario autenticado
        
    Returns:
        Lista de órdenes del usuario
    """
    orders = await service.get_user_orders(current_user.id)
    
    # Convertir a OrderResponse
    orders_response = []
    for order in orders:
        items_response = [
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal))
            )
            for item in order.order_items
        ]
        
        orders_response.append(
            OrderResponse(
                id=order.id,
                order_number=order.order_number,
                status=order.status,
                total=Decimal(str(order.total)),
                created_at=order.created_at,
                items=items_response,
                shipping_address=order.shipping_address,
                shipping_city=order.shipping_city
            )
        )
    
    return orders_response


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse,
    summary="Actualizar estado de orden"
)
async def update_order_status(
    order_id: int,
    status_in: OrderUpdateStatus,
    service: Annotated[OrderService, Depends(get_order_service)],
    current_admin: Annotated[User, Depends(get_current_admin)]
) -> OrderResponse:
    """
    Actualiza el estado de una orden. Solo accesible por administradores.
    
    Implementa una máquina de estados finita con las siguientes transiciones:
    - PENDING -> CONFIRMED o CANCELLED
    - CONFIRMED -> SHIPPED
    - SHIPPED -> DELIVERED
    
    Si se cancela una orden (status=CANCELLED) y no está DELIVERED,
    el sistema automáticamente devuelve el stock de todos los productos.
    
    Args:
        order_id: ID de la orden a actualizar
        status_in: Nuevo estado de la orden
        service: Servicio de órdenes
        current_admin: Usuario administrador autenticado
        
    Returns:
        Orden actualizada con el nuevo estado
        
    Raises:
        HTTPException: Si la orden no existe (404) o hay error en la transición
    """
    try:
        order = await service.update_status(order_id, status_in.status)
        
        # Convertir a OrderResponse
        items_response = [
            OrderItemResponse(
                product_id=item.product_id,
                product_name=item.product.name,
                quantity=item.quantity,
                unit_price=Decimal(str(item.unit_price)),
                subtotal=Decimal(str(item.subtotal))
            )
            for item in order.order_items
        ]
        
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            total=Decimal(str(order.total)),
            created_at=order.created_at,
            items=items_response,
            shipping_address=order.shipping_address,
            shipping_city=order.shipping_city
        )
    except HTTPException:
        # Re-lanzar excepciones HTTP tal cual
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al actualizar el estado de la orden: {str(e)}"
        )
