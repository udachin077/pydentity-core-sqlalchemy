import uuid

import pytest
from pydentity.security.claims import ClaimsPrincipal, ClaimsIdentity, Claim, ClaimTypes
from sqlalchemy.exc import IntegrityError

from pydentity_db_sqlalchemy.exc import RoleNotFound
from pydentity_db_sqlalchemy.models import IdentityUser


@pytest.fixture
def principal(user):
    return ClaimsPrincipal(
        ClaimsIdentity(
            claims=[
                Claim(ClaimTypes.Name, user.username),
                Claim(ClaimTypes.Email, user.email),
                Claim(ClaimTypes.NameIdentifier, user.id),
            ],
            authentication_type="App"
        )
    )


@pytest.mark.asyncio
async def test_all(user_store):
    assert len(await user_store.all()) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize("_user", {
    IdentityUser(email="test_username@email.com", username="test_username@email.com".upper())
})
async def test_create(user_store, _user):
    create_result = await user_store.create(_user)
    assert create_result.succeeded is True


@pytest.mark.asyncio
@pytest.mark.parametrize("_user", {
    IdentityUser(email="alex@email.com", username="alex@email.com".upper())
})
async def test_create_raise(user_store, _user):
    with pytest.raises(IntegrityError):
        await user_store.create(_user)


@pytest.mark.asyncio
async def test_update(user_store, user):
    user_store.session.add(user)
    update_result = await user_store.update(user)
    assert update_result.succeeded is True


@pytest.mark.asyncio
async def test_delete(user_store, user):
    delete_result = await user_store.delete(user)
    assert delete_result.succeeded is True


@pytest.mark.asyncio
async def test_find_by_id(user_store, user):
    find_result_1 = await user_store.find_by_id(user.id)
    find_result_2 = await user_store.find_by_id(str(uuid.uuid4()))
    assert bool(find_result_1) is True
    assert bool(find_result_2) is False


@pytest.mark.asyncio
@pytest.mark.parametrize("name, result", {
    ("alex@email.com".upper(), True,),
    ("alex@email.com", False,),
    ("test@email.com", False,),
})
async def test_find_by_name(user_store, name, result):
    find_result = await user_store.find_by_name(name)
    assert bool(find_result) is result


@pytest.mark.asyncio
@pytest.mark.parametrize("email, result", {
    ("alex@email.com".upper(), True,),
    ("alex@email.com", False,),
    ("test@email.com", False,),
})
async def test_find_by_email(user_store, email, result):
    find_result = await user_store.find_by_email(email)
    assert bool(find_result) is result


@pytest.mark.asyncio
async def test_add_to_role(user_store, user):
    await user_store.add_to_role(user, "admin".upper())


@pytest.mark.asyncio
async def test_add_to_role_raise(user_store, user):
    with pytest.raises(RoleNotFound):
        await user_store.add_to_role(user, "test".upper())


@pytest.mark.asyncio
async def test_get_roles(user_store, user):
    roles = await user_store.get_roles(user)
    assert len(roles) == 1


@pytest.mark.asyncio
async def test_get_users_in_role():
    assert False


@pytest.mark.asyncio
async def test_is_in_role():
    assert False


@pytest.mark.asyncio
async def test_remove_from_role():
    assert False


@pytest.mark.asyncio
async def test_add_login():
    assert False


@pytest.mark.asyncio
async def test_find_by_login():
    assert False


@pytest.mark.asyncio
async def test_get_logins():
    assert False


@pytest.mark.asyncio
async def test_remove_login():
    assert False


@pytest.mark.asyncio
async def test_get_token():
    assert False


@pytest.mark.asyncio
async def test_remove_token():
    assert False


@pytest.mark.asyncio
async def test_set_token():
    assert False


@pytest.mark.asyncio
async def test_get_two_factor_enabled():
    assert False


@pytest.mark.asyncio
async def test_set_two_factor_enabled():
    assert False


@pytest.mark.asyncio
async def test_get_authenticator_key():
    assert False


@pytest.mark.asyncio
async def test_set_authenticator_key():
    assert False


@pytest.mark.asyncio
async def test_count_codes():
    assert False


@pytest.mark.asyncio
async def test_redeem_code():
    assert False


@pytest.mark.asyncio
async def test_replace_codes():
    assert False


@pytest.mark.asyncio
async def test_add_claims():
    assert False


@pytest.mark.asyncio
async def test_get_claims():
    assert False


@pytest.mark.asyncio
async def test_get_users_for_claim():
    assert False


@pytest.mark.asyncio
async def test_remove_claims():
    assert False


@pytest.mark.asyncio
async def test_replace_claim():
    assert False
