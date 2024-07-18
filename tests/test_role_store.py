import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from pydentity_db_sqlalchemy.models import IdentityRole


@pytest.mark.asyncio
async def test_all(role_store):
    roles = await role_store.all()
    assert len(roles) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("_role", {
    IdentityRole(name="test_role", normalized_name="test_role".upper())
})
async def test_create(role_store, _role):
    create_result = await role_store.create(_role)
    assert create_result.succeeded is True


@pytest.mark.asyncio
@pytest.mark.parametrize("_role", {
    IdentityRole(name="admin", normalized_name="admin".upper()),
    IdentityRole(name="test_role", normalized_name="admin".upper()),
})
async def test_create_raise(role_store, _role):
    with pytest.raises(IntegrityError):
        await role_store.create(_role)


@pytest.mark.asyncio
async def test_update(role_store, role):
    role_store.session.add(role)
    update_result = await role_store.update(role)
    assert update_result.succeeded is True


@pytest.mark.asyncio
async def test_delete(role_store, role):
    delete_result = await role_store.delete(role)
    assert delete_result.succeeded is True


@pytest.mark.asyncio
async def test_find_by_id(role_store, role):
    find_result_1 = await role_store.find_by_id(role.id)
    find_result_2 = await role_store.find_by_id(str(uuid.uuid4()))
    assert bool(find_result_1) is True
    assert bool(find_result_2) is False


@pytest.mark.asyncio
@pytest.mark.parametrize("name, result", {
    ("admin".upper(), True,),
    ("admin", False,),
    ("test", False,),
})
async def test_find_by_name(role_store, name, result):
    find_result = await role_store.find_by_name(name)
    assert bool(find_result) is result
