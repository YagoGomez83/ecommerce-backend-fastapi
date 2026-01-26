import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


# Leer la URL de la base de datos desde variable de entorno
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:secret@localhost:5432/ecommerce_db")

# Convertir la URL a formato asíncrono si es necesario
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)


# Crear el engine asíncrono de SQLAlchemy
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Cambiar a False en producción
    future=True,
    pool_pre_ping=True,  # Verificar conexiones antes de usarlas
    pool_size=10,
    max_overflow=20,
)


# Crear sessionmaker asíncrona
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# Función auxiliar para inyectar la sesión en las rutas de FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency para inyectar la sesión de base de datos en las rutas de FastAPI.
    
    Uso:
        @app.get("/items")
        async def get_items(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


# Función para crear todas las tablas (útil para desarrollo)
async def create_tables():
    """
    Crea todas las tablas en la base de datos.
    Solo para desarrollo. En producción usar Alembic para migraciones.
    """
    from app.infrastructure.database.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# Función para eliminar todas las tablas (útil para testing)
async def drop_tables():
    """
    Elimina todas las tablas de la base de datos.
    CUIDADO: Solo usar en desarrollo/testing.
    """
    from app.infrastructure.database.models import Base
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
