"""
Módulo de repositorio base genérico para operaciones CRUD.

Este módulo implementa el patrón Repository con genéricos de Python,
permitiendo reutilizar la lógica CRUD para cualquier modelo de SQLAlchemy.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any, Type, Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import DeclarativeBase
from pydantic import BaseModel


# TypeVar para el modelo de SQLAlchemy (debe heredar de DeclarativeBase)
ModelType = TypeVar("ModelType", bound=DeclarativeBase)

# TypeVar para el esquema Pydantic usado en creación
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)

# TypeVar para el esquema Pydantic usado en actualización
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Repositorio base genérico para operaciones CRUD asíncronas.
    
    Esta clase implementa el patrón Repository proporcionando métodos CRUD
    genéricos que pueden ser utilizados con cualquier modelo de SQLAlchemy.
    
    Args:
        model: La clase del modelo de SQLAlchemy (ej: User, Product)
        db: Sesión asíncrona de SQLAlchemy
    
    Example:
        ```python
        user_repo = BaseRepository(User, db_session)
        new_user = await user_repo.create(user_schema)
        ```
    """

    def __init__(self, model: Type[ModelType], db: AsyncSession):
        """
        Inicializa el repositorio con el modelo y la sesión de base de datos.
        
        Args:
            model: Clase del modelo de SQLAlchemy a utilizar
            db: Sesión asíncrona de SQLAlchemy para ejecutar las queries
        """
        self.model = model
        self.db = db

    async def create(self, schema: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """
        Crea una nueva entidad en la base de datos.
        
        Este método acepta tanto un modelo Pydantic como un diccionario,
        crea una instancia del modelo SQLAlchemy, la persiste en la base de datos
        y retorna la entidad creada con su ID generado.
        
        Args:
            schema: Esquema Pydantic o diccionario con los datos de la entidad
        
        Returns:
            La entidad creada con todos sus campos, incluyendo ID y timestamps
        
        Example:
            ```python
            user_data = UserCreate(email="test@example.com", username="test")
            new_user = await repo.create(user_data)
            print(new_user.id)  # ID generado automáticamente
            ```
        """
        # Convertir el esquema Pydantic a diccionario si es necesario
        if isinstance(schema, BaseModel):
            data = schema.model_dump(exclude_unset=True)
        else:
            data = schema
        
        # Crear la instancia del modelo
        db_obj = self.model(**data)
        
        # Agregar a la sesión y hacer commit
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        return db_obj

    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Busca una entidad por su ID.
        
        Utiliza el estilo moderno de SQLAlchemy 2.0 con select statements.
        
        Args:
            id: ID de la entidad a buscar
        
        Returns:
            La entidad encontrada o None si no existe
        
        Example:
            ```python
            user = await repo.get_by_id(1)
            if user:
                print(user.email)
            ```
        """
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Obtiene una lista paginada de todas las entidades.
        
        Implementa paginación mediante offset (skip) y limit para manejar
        grandes volúmenes de datos de forma eficiente.
        
        Args:
            skip: Número de registros a omitir (offset). Default: 0
            limit: Número máximo de registros a retornar. Default: 100
        
        Returns:
            Lista de entidades encontradas (puede ser vacía)
        
        Example:
            ```python
            # Obtener los primeros 10 usuarios
            users = await repo.get_all(skip=0, limit=10)
            
            # Obtener la segunda página (usuarios 10-20)
            users_page2 = await repo.get_all(skip=10, limit=10)
            ```
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self, 
        id: int, 
        schema: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> Optional[ModelType]:
        """
        Actualiza una entidad existente en la base de datos.
        
        Busca la entidad por ID y actualiza solo los campos proporcionados
        en el esquema. Si la entidad no existe, retorna None.
        
        Args:
            id: ID de la entidad a actualizar
            schema: Esquema Pydantic o diccionario con los campos a actualizar
        
        Returns:
            La entidad actualizada o None si no fue encontrada
        
        Example:
            ```python
            update_data = UserUpdate(email="newemail@example.com")
            updated_user = await repo.update(1, update_data)
            if updated_user:
                print(f"Email actualizado a: {updated_user.email}")
            ```
        """
        # Buscar la entidad existente
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        
        # Convertir el esquema a diccionario si es necesario
        if isinstance(schema, BaseModel):
            update_data = schema.model_dump(exclude_unset=True)
        else:
            update_data = schema
        
        # Actualizar los atributos de la entidad
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        # Hacer commit y refrescar
        await self.db.commit()
        await self.db.refresh(db_obj)
        
        return db_obj

    async def delete(self, id: int) -> bool:
        """
        Elimina una entidad de la base de datos.
        
        Utiliza el estilo moderno de SQLAlchemy 2.0 con delete statements.
        Retorna True si la entidad fue eliminada, False si no existía.
        
        Args:
            id: ID de la entidad a eliminar
        
        Returns:
            True si la entidad fue eliminada, False si no fue encontrada
        
        Example:
            ```python
            was_deleted = await repo.delete(1)
            if was_deleted:
                print("Usuario eliminado exitosamente")
            else:
                print("Usuario no encontrado")
            ```
        """
        # Verificar si la entidad existe
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        
        # Eliminar la entidad
        await self.db.delete(db_obj)
        await self.db.commit()
        
        return True

    async def count(self) -> int:
        """
        Cuenta el número total de entidades en la tabla.
        
        Útil para implementar paginación con información del total de páginas.
        
        Returns:
            Número total de registros en la tabla
        
        Example:
            ```python
            total_users = await repo.count()
            total_pages = (total_users + limit - 1) // limit
            ```
        """
        from sqlalchemy import func
        stmt = select(func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return result.scalar_one()

    async def exists(self, id: int) -> bool:
        """
        Verifica si existe una entidad con el ID especificado.
        
        Más eficiente que get_by_id cuando solo necesitas verificar existencia.
        
        Args:
            id: ID de la entidad a verificar
        
        Returns:
            True si la entidad existe, False en caso contrario
        
        Example:
            ```python
            if await repo.exists(1):
                print("El usuario existe")
            ```
        """
        stmt = select(self.model.id).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
