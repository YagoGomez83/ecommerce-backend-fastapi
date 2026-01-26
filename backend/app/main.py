from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.infrastructure.database.database import create_tables
from app.infrastructure.api.v1.endpoints import users, login, products, stock, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Ciclo de vida de la aplicación.
    Se ejecuta al iniciar y al cerrar la aplicación.
    """
    # Startup: Crear tablas en la base de datos
    print("🚀 Iniciando aplicación...")
    print("📦 Creando tablas en la base de datos...")
    await create_tables()
    print("✅ Tablas creadas exitosamente")
    
    yield
    
    # Shutdown: Limpiar recursos si es necesario
    print("🛑 Cerrando aplicación...")


app = FastAPI(
    title="Ecommerce Pro API",
    description="API para sistema de e-commerce profesional",
    version="1.0.0",
    lifespan=lifespan
)

# Incluir routers
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(login.router, prefix="/api/v1/login", tags=["login"])
app.include_router(products.router, prefix="/api/v1/products", tags=["products"])
app.include_router(stock.router, prefix="/api/v1/stock", tags=["stock"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])


@app.get("/")
def read_root():
    return {
        "message": "Bienvenido a la API de E-commerce",
        "status": "online"
    }
