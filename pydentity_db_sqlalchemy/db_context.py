from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator, Type

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession

from pydentity_db_sqlalchemy.models import DbModel


class SQLAlchemyDbContext:
    def __init__(
            self,
            engine: AsyncEngine,
            class_: Type[AsyncSession] = AsyncSession,
            autoflush: bool = True,
            expire_on_commit: bool = True,
            info: Optional[dict] = None,
            **kwargs
    ):
        self.async_engine = engine
        self.async_session_maker = async_sessionmaker(
            self.async_engine,
            class_=class_,
            autoflush=autoflush,
            expire_on_commit=expire_on_commit,
            info=info,
            **kwargs
        )

    async def ensure_created(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(DbModel.metadata.create_all)

    async def ensure_deleted(self):
        async with self.async_engine.begin() as conn:
            await conn.run_sync(DbModel.metadata.drop_all)

    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session_maker() as session:
            yield session
