"""
Endpoints para operaciones relacionadas con productos.
"""

from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.product import ProductCreate, ProductResponse
from app.application.services.product_service import ProductService
from app.infrastructure.api.v1.deps import get_product_service, get_current_admin
from app.infrastructure.database.models import User


router = APIRouter()


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear producto (Solo admins)"
)
async def create_product(
    product_in: ProductCreate,
    service: Annotated[ProductService, Depends(get_product_service)],
    current_admin: Annotated[User, Depends(get_current_admin)]
) -> ProductResponse:
    """
    Crea un nuevo producto. Solo accesible por administradores.
    
    Args:
        product_in: Datos del producto a crear
        service: Servicio de productos
        current_admin: Usuario administrador autenticado
        
    Returns:
        Producto creado
        
    Raises:
        HTTPException: Si el SKU ya existe (status 400)
    """
    try:
        product = await service.create_product(product_in)
        return product
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "/trending",
    response_model=List[ProductResponse],
    summary="Obtener productos más visitados (Público)"
)
async def get_trending_products(
    service: Annotated[ProductService, Depends(get_product_service)],
    limit: int = 5
) -> List[ProductResponse]:
    """
    Obtiene los productos más visitados (tendencias). Acceso público.
    
    Args:
        service: Servicio de productos
        limit: Número máximo de productos a retornar (default 5)
        
    Returns:
        Lista de productos ordenados por popularidad
    """
    products = await service.get_trending_products(limit)
    return products


@router.get(
    "/{id}",
    response_model=ProductResponse,
    summary="Obtener producto por ID (Público)"
)
async def get_product_by_id(
    id: int,
    service: Annotated[ProductService, Depends(get_product_service)]
) -> ProductResponse:
    """
    Obtiene un producto por su ID. Acceso público.
    
    Registra automáticamente la visita al producto para análisis de tendencias.
    
    Args:
        id: ID del producto a obtener
        service: Servicio de productos
        
    Returns:
        Producto encontrado
        
    Raises:
        HTTPException: Si el producto no existe (status 404)
    """
    product = await service.get_product_by_id(id)
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {id} no encontrado"
        )
    
    return product
