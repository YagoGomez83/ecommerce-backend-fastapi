"""
Repositorio para gestionar operaciones CRUD de productos.
"""

from typing import List

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.repository import BaseRepository
from app.infrastructure.database.models import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(BaseRepository[Product, ProductCreate, ProductUpdate]):
    """
    Repositorio para operaciones relacionadas con productos.
    
    Hereda de BaseRepository proporcionando todas las operaciones CRUD básicas
    para el modelo Product, además de métodos especializados para análisis de tendencias.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Inicializa el repositorio de productos.
        
        Args:
            db: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(Product, db)
    
    async def get_by_sku(self, sku: str) -> Product | None:
        """
        Obtiene un producto por su SKU.
        
        Args:
            sku: Código SKU del producto
            
        Returns:
            Producto si existe, None en caso contrario
        """
        stmt = select(Product).where(Product.sku == sku)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def increment_views(self, product_id: int) -> None:
        """
        Incrementa el contador de visitas de un producto.
        
        Este método ejecuta una consulta SQL directa para incrementar
        atómicamente el contador de visitas. Es crucial para el análisis
        de tendencias y comportamiento de usuarios.
        
        Args:
            product_id: ID del producto a incrementar
        """
        # Asegúrate que el nombre de la columna coincida con el modelo
        stmt = text("UPDATE products SET views_count = views_count + 1 WHERE id = :id")
        await self.db.execute(stmt, {"id": product_id})
        await self.db.commit()
    
    async def get_trending(self, limit: int = 5) -> List[Product]:
        """
        Obtiene los productos más visitados (tendencias).
        
        Retorna una lista de productos ordenados por el número de visitas
        en orden descendente. Útil para mostrar productos populares y
        análisis de tendencias.
        
        Args:
            limit: Número máximo de productos a retornar (default 5)
            
        Returns:
            Lista de productos ordenados por views_count descendente
        """
        stmt = select(Product).where(
            Product.is_active == True
        ).order_by(
            Product.views_count.desc()
        ).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
