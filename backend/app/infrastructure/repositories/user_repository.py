"""
Repositorio para gestionar operaciones CRUD de usuarios.
"""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repository import BaseRepository
from app.infrastructure.database.models import User
from app.schemas.user import UserCreate, UserUpdate


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repositorio para operaciones relacionadas con usuarios.
    
    Hereda de BaseRepository proporcionando todas las operaciones CRUD básicas
    para el modelo User.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio de usuarios.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(User, db)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Busca un usuario por su email.
        
        Args:
            email: Email del usuario a buscar
            
        Returns:
            Usuario encontrado o None si no existe
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """
        Busca un usuario por su username.
        
        Args:
            username: Username del usuario a buscar
            
        Returns:
            Usuario encontrado o None si no existe
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
