"""
Endpoints para operaciones relacionadas con usuarios.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.user import UserCreate, UserResponse
from app.application.services.user_service import UserService
from app.infrastructure.api.v1.deps import get_user_service


router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user(
    user_in: UserCreate,
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """
    Crea un nuevo usuario.
    
    Args:
        user_in: Datos del usuario a crear
        service: Servicio de usuarios
        
    Returns:
        Usuario creado
        
    Raises:
        HTTPException: Si el usuario ya existe (status 400)
    """
    try:
        user = await service.create_user(user_in)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
