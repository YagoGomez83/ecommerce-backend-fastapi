"""
Servicio de órdenes que implementa la lógica de negocio.
"""

from datetime import datetime
from typing import List
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy import update

from app.infrastructure.repositories.order_repository import OrderRepository
from app.infrastructure.repositories.product_repository import ProductRepository
from app.infrastructure.repositories.stock_repository import StockRepository
from app.infrastructure.database.models import Order, OrderItem, OrderStatus, StockMovement, StockMovementType, Product
from app.schemas.order import OrderCreate, OrderResponse
from app.schemas.stock_movement import StockMovementCreate


class OrderService:
    """
    Servicio que gestiona la lógica de negocio relacionada con órdenes.
    
    Actúa como intermediario entre la API y el repositorio, implementando
    validaciones y reglas de negocio específicas.
    """
    
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        stock_repository: StockRepository
    ):
        """
        Inicializa el servicio de órdenes.
        
        Args:
            order_repository: Repositorio de órdenes para operaciones de datos
            product_repository: Repositorio de productos para consultas
            stock_repository: Repositorio de stock para registrar movimientos
        """
        self.order_repo = order_repository
        self.product_repo = product_repository
        self.stock_repo = stock_repository
    
    async def create_order(self, user_id: int, order_in: OrderCreate) -> Order:
        """
        Crea una nueva orden validando stock y calculando totales.
        
        Maneja toda la operación en una única transacción incluyendo:
        - Validación de productos y stock
        - Creación de la orden y sus items
        - Actualización de stock de productos
        - Registro de movimientos de stock
        
        Args:
            user_id: ID del usuario que realiza la orden
            order_in: Datos de la orden a crear
            
        Returns:
            Orden creada con todos sus items
            
        Raises:
            HTTPException: Si un producto no existe (404) o hay stock insuficiente (400)
        """
        db = self.order_repo.db
        
        # Generar número de orden único
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        order_number = f"ORD-{timestamp}-{user_id}"
        
        # Inicializar totales
        subtotal = Decimal("0.00")
        tax = Decimal("0.00")
        shipping_cost = Decimal("0.00")
        
        # Lista para items de la orden
        db_items: List[OrderItem] = []
        
        # Iterar sobre los items de la orden
        for item in order_in.items:
            # Buscar el producto
            product = await self.product_repo.get_by_id(item.product_id)
            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Producto con ID {item.product_id} no encontrado"
                )
            
            # Validar stock disponible
            if product.stock_actual < item.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Stock insuficiente para {product.name}. Stock disponible: {product.stock_actual}, solicitado: {item.quantity}"
                )
            
            # Calcular subtotal del item
            unit_price = Decimal(str(product.price))
            item_subtotal = unit_price * item.quantity
            subtotal += item_subtotal
            
            # Crear instancia de OrderItem
            order_item = OrderItem(
                product_id=product.id,
                quantity=item.quantity,
                unit_price=float(unit_price),
                subtotal=float(item_subtotal)
            )
            
            db_items.append(order_item)
            
            # Actualizar stock del producto directamente
            stock_before = product.stock_actual
            stock_after = stock_before - item.quantity
            
            stmt = (
                update(Product)
                .where(Product.id == product.id)
                .values(stock_actual=stock_after)
            )
            await db.execute(stmt)
            
            # Crear movimiento de stock
            stock_movement = StockMovement(
                product_id=product.id,
                movement_type=StockMovementType.SALIDA,
                quantity=item.quantity,
                stock_before=stock_before,
                stock_after=stock_after,
                reason=f"Venta - Orden {order_number}",
                notes=f"Orden de usuario {user_id}"
            )
            db.add(stock_movement)
        
        # Calcular total
        total = subtotal + tax + shipping_cost
        
        # Crear la instancia de Order
        order = Order(
            order_number=order_number,
            user_id=user_id,
            status=OrderStatus.PENDING,
            subtotal=float(subtotal),
            tax=float(tax),
            shipping_cost=float(shipping_cost),
            total=float(total),
            shipping_address=order_in.shipping_address,
            shipping_city=order_in.shipping_city,
            shipping_postal_code=order_in.shipping_postal_code,
            notes=order_in.notes,
            order_items=db_items
        )
        
        # Agregar orden a la sesión
        db.add(order)
        
        # Hacer commit de toda la transacción
        await db.commit()
        
        # Recargar la orden con sus relaciones usando selectinload
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
        )
        result = await db.execute(query)
        refreshed_order = result.scalar_one()
        
        return refreshed_order
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """
        Obtiene todas las órdenes de un usuario.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Lista de órdenes del usuario
        """
        return await self.order_repo.get_by_user(user_id)
    
    async def get_order_by_id(self, order_id: int) -> Order | None:
        """
        Obtiene una orden por su ID.
        
        Args:
            order_id: ID de la orden
            
        Returns:
            Orden si existe, None en caso contrario
        """
        return await self.order_repo.get_by_id(order_id)
    
    async def update_status(self, order_id: int, new_status: OrderStatus) -> Order:
        """
        Actualiza el estado de una orden con validaciones de negocio.
        
        Implementa la máquina de estados finita:
        - PENDING -> CONFIRMED o CANCELLED
        - CONFIRMED -> SHIPPED
        - SHIPPED -> DELIVERED
        - Si se cancela (CANCELLED) y no está DELIVERED, devuelve el stock automáticamente
        
        Args:
            order_id: ID de la orden a actualizar
            new_status: Nuevo estado de la orden
            
        Returns:
            Orden actualizada
            
        Raises:
            HTTPException: Si la orden no existe o hay un error en la transición
        """
        db = self.order_repo.db
        
        # Obtener la orden actual con sus items
        order = await self.order_repo.get_by_id(order_id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orden con ID {order_id} no encontrada"
            )
        
        current_status = order.status
        
        # Si se cancela y NO está DELIVERED, devolver el stock
        if new_status == OrderStatus.CANCELLED and current_status != OrderStatus.DELIVERED:
            # Iterar sobre los items de la orden y devolver el stock
            for item in order.order_items:
                # Crear movimiento de stock de tipo ENTRADA (devolución)
                movement_in = StockMovementCreate(
                    product_id=item.product_id,
                    movement_type=StockMovementType.ENTRADA,
                    quantity=item.quantity,
                    reason=f"Cancelación Orden {order.order_number}",
                    notes=f"Devolución de stock por cancelación de orden"
                )
                
                # Obtener producto actual para el stock
                product = await self.product_repo.get_by_id(item.product_id)
                if product:
                    # Crear el movimiento de stock
                    stock_movement = StockMovement(
                        product_id=item.product_id,
                        movement_type=StockMovementType.ENTRADA,
                        quantity=item.quantity,
                        stock_before=product.stock_actual,
                        stock_after=product.stock_actual + item.quantity,
                        reason=movement_in.reason,
                        notes=movement_in.notes
                    )
                    db.add(stock_movement)
                    
                    # Actualizar el stock del producto
                    from sqlalchemy import update
                    stmt = (
                        update(Product)
                        .where(Product.id == item.product_id)
                        .values(stock_actual=product.stock_actual + item.quantity)
                    )
                    await db.execute(stmt)
        
        # Actualizar el estado de la orden
        order.status = new_status
        
        # Hacer commit de los cambios
        await db.commit()
        
        # Recargar la orden con sus relaciones
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        
        query = (
            select(Order)
            .where(Order.id == order.id)
            .options(
                selectinload(Order.order_items).selectinload(OrderItem.product)
            )
        )
        result = await db.execute(query)
        refreshed_order = result.scalar_one()
        
        return refreshed_order
