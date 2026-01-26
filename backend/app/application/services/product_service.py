"""
Servicio de productos que implementa la lógica de negocio.
"""

from typing import List

from app.infrastructure.repositories.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.infrastructure.database.models import Product


class ProductService:
    """
    Servicio que gestiona la lógica de negocio relacionada con productos.
    
    Actúa como intermediario entre la API y el repositorio, implementando
    validaciones y reglas de negocio específicas.
    """
    
    def __init__(self, product_repository: ProductRepository):
        """
        Inicializa el servicio de productos.
        
        Args:
            product_repository: Repositorio de productos para operaciones de datos
        """
        self.repo = product_repository
    
    async def create_product(self, schema: ProductCreate) -> Product:
        """
        Crea un nuevo producto verificando que el SKU no exista.
        
        Args:
            schema: Datos del producto a crear
            
        Returns:
            Producto creado
            
        Raises:
            ValueError: Si el SKU ya existe en la base de datos
        """
        # Verificar si el SKU ya existe
        existing_product = await self.repo.get_by_sku(schema.sku)
        if existing_product:
            raise ValueError(f"Ya existe un producto con el SKU: {schema.sku}")
        
        # Crear el producto
        return await self.repo.create(schema)
    
    async def get_product_by_id(self, id: int) -> Product | None:
        """
        Obtiene un producto por ID e incrementa su contador de visitas.
        
        Este método registra automáticamente la visita al producto como
        efecto secundario para análisis de tendencias.
        
        Args:
            id: ID del producto a obtener
            
        Returns:
            Producto si existe, None en caso contrario
        """
        product = await self.repo.get_by_id(id)
        
        if product:
            # Registrar la visita (side effect)
            await self.repo.increment_views(id)
        
        return product
    
    async def get_trending_products(self, limit: int = 5) -> List[Product]:
        """
        Obtiene los productos más visitados (tendencias).
        
        Args:
            limit: Número máximo de productos a retornar (default 5)
            
        Returns:
            Lista de productos ordenados por popularidad
        """
        return await self.repo.get_trending(limit)
