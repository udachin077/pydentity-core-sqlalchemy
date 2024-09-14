from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from pydenticore.security.claims import Claim
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError

from pydentity_db_sqlalchemy.models import IdentityRole, IdentityRoleClaim
from pydentity_db_sqlalchemy.stores.role_store import RoleStore


@pytest_asyncio.fixture(autouse=True)
async def clear(session):
    await session.execute(delete(IdentityRole))


@pytest_asyncio.fixture
async def store(session) -> AsyncGenerator[RoleStore, None]:
    RoleStore.role_model = IdentityRole
    RoleStore.role_claim_model = IdentityRoleClaim
    yield RoleStore(session)


@pytest.mark.asyncio
async def test_all(store, session):
    session.add_all([
        IdentityRole(name='admin', normalized_name='ADMIN'),
        IdentityRole(name='user', normalized_name='USER'),
        IdentityRole(name='guest', normalized_name='GUEST'),
    ])
    await session.commit()
    assert len(await store.all()) == 3


@pytest.mark.asyncio
async def test_create(store, session):
    role = IdentityRole(name='test_create', normalized_name='test_create'.upper())
    result = await store.create(role)
    assert result.succeeded is True
    found = await session.execute(
        select(IdentityRole).where(IdentityRole.normalized_name == 'test_create'.upper())  # type: ignore
    )
    assert len(found.all()) == 1

    with pytest.raises(IntegrityError):
        role = IdentityRole(name='test_create', normalized_name='test_create'.upper())
        await store.create(role)


@pytest.mark.asyncio
async def test_update(store, session):
    session.add(IdentityRole(name='test_update', normalized_name='test_update'.upper()))
    await session.commit()
    found = await session.execute(
        select(IdentityRole).where(IdentityRole.normalized_name == 'test_update'.upper())  # type: ignore
    )
    role: IdentityRole = found.scalar_one_or_none()

    role.name = 'UpdatedRole'
    role.normalized_name = 'UPDATEDROLE'
    assert role.concurrency_stamp is None
    result = await store.update(role)
    assert result.succeeded is True
    assert role.concurrency_stamp is not None


@pytest.mark.asyncio
async def test_delete(store, session):
    session.add(IdentityRole(name='test_delete', normalized_name='test_delete'.upper()))
    await session.commit()
    found = await session.execute(
        select(IdentityRole).where(IdentityRole.normalized_name == 'test_delete'.upper())  # type: ignore
    )
    role: IdentityRole = found.scalar_one_or_none()

    result = await store.delete(role)
    assert result.succeeded is True
    re_found = await session.execute(
        select(IdentityRole).where(IdentityRole.normalized_name == 'test_delete'.upper())  # type: ignore
    )
    assert re_found.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_find_by_id(store, session):
    role = IdentityRole(name='test_find_by_id', normalized_name='test_find_by_id'.upper())
    session.add(role)
    await session.commit()

    found = await store.find_by_id(role.id)
    assert found is not None and found.name == 'test_find_by_id'
    assert await store.find_by_id(str(uuid4())) is None


@pytest.mark.asyncio
async def test_find_by_name(store, session):
    role = IdentityRole(name='test_find_by_name', normalized_name='test_find_by_name'.upper())
    session.add(role)
    await session.commit()

    found = await store.find_by_name('test_find_by_name'.upper())
    assert found is not None
    assert await store.find_by_name('UNDEFINED') is None


@pytest.mark.asyncio
async def test_claim(store, session):
    role = IdentityRole(name='test_claim', normalized_name='test_claim'.upper())
    session.add(role)
    await session.commit()

    await store.add_claim(role, Claim("Name", 'test_claim'))
    await store.add_claim(role, Claim("Name", 'test_claim'))
    await store.add_claim(role, Claim("Email", 'test_claim@email.com'))

    claims = await store.get_claims(role)
    assert len(claims) == 3

    await store.remove_claim(role, Claim("Email", 'test_claim@email.com'))
    claims = await store.get_claims(role)
    assert len(claims) == 2

    await store.remove_claim(role, Claim("Name", 'test_claim'))
    claims = await store.get_claims(role)
    assert len(claims) == 0
