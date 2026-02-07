# Product Backlog - Ecommerce Pro

## Sprint 1: Infraestructura y Modelado (COMPLETADO ✅)
- [x] Configuración de Docker (Postgres).
- [x] Modelos de Base de Datos (SQLAlchemy).
- [x] Creación automática de tablas (Lifespan).

## Sprint 2: Capa de Acceso a Datos (COMPLETADO ✅)
- [x] Implementar Repositorio Genérico (BaseRepository).
- [x] Implementar Repositorios Específicos (UserRepository, ProductRepository, StockRepository, OrderRepository).
- [x] Definir Schemas Pydantic (Validación de datos).

## Sprint 3: API de Autenticación (COMPLETADO ✅)
- [x] Implementar JWT (Tokens de acceso).
- [x] Endpoint de Login (/api/v1/login).
- [x] Sistema de Hashing de contraseñas (bcrypt).
- [x] Middleware de autenticación (get_current_user).

## Sprint 4: CRUD de Productos (COMPLETADO ✅)
- [x] Endpoint GET /api/v1/products (Listar productos).
- [x] Endpoint POST /api/v1/products (Crear producto - Admin).
- [x] Endpoint PUT /api/v1/products/{id} (Actualizar producto - Admin).
- [x] Endpoint DELETE /api/v1/products/{id} (Eliminar producto - Admin).

## Sprint 5: Gestión de Stock (COMPLETADO ✅)
- [x] Endpoint GET /api/v1/stock/movements (Historial de movimientos).
- [x] Endpoint POST /api/v1/stock/movement (Registrar entrada/salida manual).
- [x] Integración automática con creación de órdenes.
- [x] Sistema de trazabilidad de stock.

## Sprint 6: Sistema de Órdenes de Compra (COMPLETADO ✅)
- [x] Endpoint POST /api/v1/orders (Crear orden de compra).
- [x] Endpoint GET /api/v1/orders (Listar órdenes del usuario).
- [x] Endpoint PUT /api/v1/orders/{id}/cancel (Cancelar orden).
- [x] Integración automática con stock (descuento y devolución).
- [x] Sistema de estados (pending, completed, cancelled).

## Sprint 7: Frontend - Inicialización (EN CURSO 🚀)
- [x] Inicializar proyecto Vite + React + TypeScript.
- [x] Crear Dockerfile para frontend (node:18-alpine).
- [x] Configurar servicio frontend en docker-compose.yml.
- [x] Configurar hot-reload para desarrollo.
- [ ] Verificar frontend corriendo en http://localhost:5173.

## Backlog Futuro 📋
- [ ] Frontend: Página de login.
- [ ] Frontend: Catálogo de productos.
- [ ] Frontend: Carrito de compras.
- [ ] Frontend: Historial de órdenes.
- [ ] Testing: Pruebas unitarias (pytest).
- [ ] Testing: Pruebas de integración.
- [ ] Deployment: CI/CD Pipeline.
- [ ] Deployment: Despliegue en producción.