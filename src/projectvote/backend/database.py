"""Database configuration and session management for the application."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .config import Settings

DATABASE_URL = "sqlite+aiosqlite:///./data/applications.db"

settings = Settings()

engine = create_async_engine(DATABASE_URL, echo=settings.db_echo)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a new database session."""
    async with AsyncSessionLocal() as session:
        yield session
