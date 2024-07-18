import os
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

from pydentity_db_sqlalchemy.db_context import SQLAlchemyDbContext
from pydentity_db_sqlalchemy.models import IdentityRole, IdentityUser
from pydentity_db_sqlalchemy.stores.role_store import RoleStore
from pydentity_db_sqlalchemy.stores.user_store import UserStore

STATIC_ROLE: IdentityRole
STATIC_USER: IdentityUser


@pytest.fixture
def role():
    return STATIC_ROLE


@pytest.fixture
def user():
    return STATIC_USER


@pytest.fixture
def db_url():
    return os.getenv("DB_URL", "sqlite+aiosqlite:///./test_sqlalchemy.db")


@pytest.fixture
def db_context(db_url):
    engine = create_async_engine(db_url)
    return SQLAlchemyDbContext(engine)


@pytest_asyncio.fixture(autouse=True)
async def init(db_context):
    admin = IdentityRole(name="admin", normalized_name="admin".upper())
    manager = IdentityRole(name="manager", normalized_name="manager".upper())
    user = IdentityRole(name="user", normalized_name="user".upper())

    alex = IdentityUser(
        username="alex@email.com",
        email="alex@email.com",
        normalized_username="alex@email.com".upper(),
        normalized_email="alex@email.com".upper(),
        roles=[user]
    )
    john = IdentityUser(
        username="john@email.com",
        email="john@email.com",
        normalized_username="john@email.com".upper(),
        normalized_email="john@email.com".upper(),
        roles=[manager, user]
    )
    anna = IdentityUser(
        username="anna@email.com",
        email="anna@email.com",
        normalized_username="anna@email.com".upper(),
        normalized_email="anna@email.com".upper(),
    )

    global STATIC_ROLE, STATIC_USER
    STATIC_ROLE, STATIC_USER = admin, alex

    await db_context.ensure_created()

    async with db_context.get_async_session() as session:
        session.add_all([alex, john, anna])
        await session.commit()
        await session.refresh(admin)
        await session.refresh(alex)

    yield

    await db_context.ensure_deleted()


@pytest_asyncio.fixture
async def role_store(db_context) -> AsyncGenerator[RoleStore, None]:
    async with db_context.get_async_session() as session:
        yield RoleStore(session)


@pytest_asyncio.fixture
async def user_store(db_context) -> AsyncGenerator[UserStore, None]:
    async with db_context.get_async_session() as session:
        yield UserStore(session)
