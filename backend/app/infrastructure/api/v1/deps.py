"""
Dependencias para los endpoints de la API.
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.infrastructure.database.database import get_db
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.stock_repository import StockRepository
from app.infrastructure.repositories.order_repository import OrderRepository
from app.application.services.user_service import UserService
from app.application.services.product_service import ProductService
from app.application.services.stock_service import StockService
from app.application.services.order_service import OrderService
from app.schemas.token import TokenPayload
from app.infrastructure.database.models import User, UserRole


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    """
    Obtiene una instancia del repositorio de usuarios.
    
    Args:
        db: Sesión de base de datos asíncrona
        
    Returns:
        Instancia de UserRepository
    """
    return UserRepository(db)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """
    Obtiene una instancia del servicio de usuarios.
    
    Args:
        user_repository: Repositorio de usuarios
        
    Returns:
        Instancia de UserService
    """
    return UserService(user_repository)


async def get_current_user(
    token: Annotated[str, Depends(reusable_oauth2)],
    user_service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    # ... (bloque try/except de decodificación igual que antes) ...
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
        
        if token_data.sub is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials"
        )
    
    # CORRECCIÓN AQUÍ: Convertimos token_data.sub a int()
    user = await user_service.user_repository.get_by_id(int(token_data.sub))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


def get_product_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> ProductRepository:
    """
    Obtiene una instancia del repositorio de productos.
    
    Args:
        db: Sesión de base de datos asíncrona
        
    Returns:
        Instancia de ProductRepository
    """
    return ProductRepository(db)


def get_product_service(
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)]
) -> ProductService:
    """
    Obtiene una instancia del servicio de productos.
    
    Args:
        product_repository: Repositorio de productos
        
    Returns:
        Instancia de ProductService
    """
    return ProductService(product_repository)


def get_stock_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> StockRepository:
    """
    Obtiene una instancia del repositorio de stock.
    
    Args:
        db: Sesión de base de datos asíncrona
        
    Returns:
        Instancia de StockRepository
    """
    return StockRepository(db)


def get_stock_service(
    stock_repository: Annotated[StockRepository, Depends(get_stock_repository)],
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)]
) -> StockService:
    """
    Obtiene una instancia del servicio de stock.
    
    Args:
        stock_repository: Repositorio de stock
        product_repository: Repositorio de productos
        
    Returns:
        Instancia de StockService
    """
    return StockService(stock_repository, product_repository)


def get_current_admin(
    current_user: Annotated[User, Depends(get_current_user)]
) -> User:
    """
    Verifica que el usuario actual sea un administrador.
    
    Args:
        current_user: Usuario autenticado
        
    Returns:
        Usuario si es administrador
        
    Raises:
        HTTPException: Si el usuario no tiene privilegios de administrador
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tiene privilegios de administrador"
        )
    return current_user


def get_order_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> OrderRepository:
    """
    Obtiene una instancia del repositorio de órdenes.
    
    Args:
        db: Sesión de base de datos asíncrona
        
    Returns:
        Instancia de OrderRepository
    """
    return OrderRepository(db)


def get_order_service(
    order_repository: Annotated[OrderRepository, Depends(get_order_repository)],
    product_repository: Annotated[ProductRepository, Depends(get_product_repository)],
    stock_repository: Annotated[StockRepository, Depends(get_stock_repository)]
) -> OrderService:
    """
    Obtiene una instancia del servicio de órdenes.
    
    Args:
        order_repository: Repositorio de órdenes
        product_repository: Repositorio de productos
        stock_repository: Repositorio de stock
        
    Returns:
        Instancia de OrderService
    """
    return OrderService(order_repository, product_repository, stock_repository)
