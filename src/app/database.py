# File: src/app/database.py
# Description: Async database session setup

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.app.config import settings

engine = create_async_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:  # type: ignore
    async with AsyncSessionLocal() as session:
        yield session