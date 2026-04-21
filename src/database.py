from typing import Annotated, AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import NullPool

from src.config import settings as s

# String used to connect to the database
DATABASE_URL = f"postgresql+asyncpg://{s.db_user}:{s.db_pass.get_secret_value()}@{s.db_host}:{s.db_port}/{s.db_name}"


class Base(DeclarativeBase):
    pass


# Engine and session factory
engine = create_async_engine(DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


session_type = Annotated[AsyncSession, Depends(get_async_session)]
