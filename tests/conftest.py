import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from pydentity_db import use_personal_data_protector
from pydentity_db.models import Model


@pytest.fixture(scope='session')
def engine():
    use_personal_data_protector()
    return create_async_engine('sqlite+aiosqlite://', echo=True)


@pytest.fixture(scope='session')
def async_session_maker(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope='session', autouse=True)
async def initialize_tests(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


@pytest_asyncio.fixture
async def session(async_session_maker):
    async with async_session_maker() as sn:
        yield sn
