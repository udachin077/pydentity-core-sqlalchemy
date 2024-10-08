from typing import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from pydentity import UserLoginInfo
from pydentity.security.claims import Claim
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from pydentity_db.models import *
from pydentity_db.stores.user_store import UserStore


async def _find_by_email(session, email: str) -> IdentityUser | None:
    found = await session.execute(
        select(IdentityUser).where(IdentityUser.normalized_email == email.upper())  # type: ignore
    )
    return found.scalar_one_or_none()


@pytest_asyncio.fixture(autouse=True)
async def clear(session):
    await session.execute(delete(IdentityUser))
    user = IdentityUser(
        email='admin@email.com',
        username='admin',
        normalized_email='admin@email.com'.upper(),
        normalized_username='admin'.upper()
    )
    session.add(user)
    await session.commit()


@pytest_asyncio.fixture
async def create_roles(session):
    session.add_all([
        IdentityRole(name='admin', normalized_name='ADMIN'),
        IdentityRole(name='user', normalized_name='USER'),
        IdentityRole(name='guest', normalized_name='GUEST'),
    ])
    await session.commit()


@pytest_asyncio.fixture
async def store(session) -> AsyncGenerator[UserStore, None]:
    UserStore.user_model = IdentityUser
    UserStore.user_role_model = IdentityUserRole
    UserStore.user_claim_model = IdentityUserClaim
    UserStore.user_token_model = IdentityUserToken
    UserStore.user_login_model = IdentityUserLogin
    UserStore.role_model = IdentityRole
    yield UserStore(session)


@pytest.mark.asyncio
async def test_all(store, session):
    session.add(
        IdentityUser(
            email='user@email.com',
            username='user',
            normalized_email='user@email.com'.upper(),
            normalized_username='user'.upper()
        )
    )
    await session.commit()
    assert len(await store.all()) == 2


@pytest.mark.asyncio
async def test_create(store, session):
    user = IdentityUser(
        email='user@email.com',
        username='user',
        normalized_email='user@email.com'.upper(),
        normalized_username='user'.upper()
    )
    result = await store.create(user)
    assert result.succeeded is True
    found = await _find_by_email(session, 'user@email.com')
    assert found is not None

    with pytest.raises(IntegrityError):
        _user = IdentityUser(
            email='admin@email.com',
            username='admin',
            normalized_email='admin@email.com'.upper(),
            normalized_username='admin'.upper()
        )
        await store.create(_user)


@pytest.mark.asyncio
async def test_update(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    user.username = 'UpdatedUser'
    user.normalized_name = 'UPDATEDUSER'
    assert user.concurrency_stamp is None
    result = await store.update(user)
    assert result.succeeded is True
    assert user.concurrency_stamp is not None


@pytest.mark.asyncio
async def test_delete(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    result = await store.delete(user)
    assert result.succeeded is True
    user = await _find_by_email(session, 'admin@email.com')
    assert user is None


@pytest.mark.asyncio
async def test_find_by(store, session):
    user = await _find_by_email(session, 'admin@email.com')

    found = await store.find_by_id(user.id)
    assert found is not None and found.username == 'admin'
    assert await store.find_by_id(str(uuid4())) is None

    found = await store.find_by_name(user.normalized_username)
    assert found is not None
    assert await store.find_by_name('UNDEFINED') is None

    found = await store.find_by_email(user.normalized_email)
    assert found is not None
    assert await store.find_by_email('UNDEFINED') is None


@pytest.mark.asyncio
async def test_user_roles(store, session, create_roles):
    user = await _find_by_email(session, 'admin@email.com')
    user_1 = IdentityUser(
        email='user@email.com',
        username='user',
        normalized_email='user@email.com'.upper(),
        normalized_username='user'.upper()
    )
    session.add(user_1)
    await session.commit()

    await store.add_to_role(user, 'ADMIN')
    await store.add_to_role(user, 'USER')
    await store.add_to_role(user_1, 'USER')

    roles = await store.get_roles(user)
    assert 'admin' in roles and 'user' in roles

    users = await store.get_users_in_role('USER')
    assert len(users) == 2

    assert await store.is_in_role(user, 'USER') is True
    assert await store.is_in_role(user, 'GUEST') is False

    await store.remove_from_role(user, 'USER')
    assert await store.is_in_role(user, 'USER') is False


@pytest.mark.asyncio
async def test_user_logins(session, store):
    user = await _find_by_email(session, 'admin@email.com')

    await store.add_login(user, UserLoginInfo('Google', 'Key'))
    await store.add_login(user, UserLoginInfo('Outlook', 'Key'))

    _user = await store.find_by_login('Google', 'Key')
    assert _user is not None
    _user = await store.find_by_login('Google', 'Key_1')
    assert _user is None
    _user = await store.find_by_login('Inbox', 'Key')
    assert _user is None

    logins = await store.get_logins(user)
    assert len(logins) == 2
    await store.remove_login(user, 'Google', 'Key')
    logins = await store.get_logins(user)
    assert len(logins) == 1
    await store.remove_login(user, 'Outlook', 'Key')
    logins = await store.get_logins(user)
    assert len(logins) == 0


@pytest.mark.asyncio
async def test_user_tokens(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    value = str(uuid4())

    await store.set_token(user, 'Application', 'auth', value)

    token = await store.get_token(user, 'Application', 'auth')
    assert token == value

    token = await store.set_token(user, 'Application', 'auth', str(uuid4()))
    assert token != value

    await store.remove_token(user, 'Application', 'auth')
    token = await store.get_token(user, 'Application', 'auth')
    assert token is None


@pytest.mark.asyncio
async def test_authenticator_key(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    value = str(uuid4())

    await store.set_authenticator_key(user, value)
    key = await store.get_authenticator_key(user)
    assert value == key


@pytest.mark.asyncio
async def test_codes(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    codes = ['JbuGcQqKeUMi', 'qrZnbnHJEIfH', 'HsWXCfJUjNNb', 'OOTRTeOJNASC', 'cqRNElOWDUrT']

    await store.replace_codes(user, *codes)
    result = await store.redeem_code(user, 'JbuGcQqKeUMi')
    assert result is True
    count = await store.count_codes(user)
    assert count == 4
    result = await store.redeem_code(user, 'qrZnbnHJEIfH')
    assert result is True
    result = await store.redeem_code(user, 'HsWXCfJUjNNb')
    assert result is True
    result = await store.redeem_code(user, 'HsWXCfJUjNNb')
    assert result is False
    count = await store.count_codes(user)
    assert count == 2


@pytest.mark.asyncio
async def test_claims(store, session):
    user = await _find_by_email(session, 'admin@email.com')
    user_1 = IdentityUser(
        email='user@email.com',
        username='user',
        normalized_email='user@email.com'.upper(),
        normalized_username='user'.upper()
    )
    session.add(user_1)
    await session.commit()
    claim = Claim('locality', 'London')

    await store.add_claims(
        user,
        Claim('name', user.username),
        Claim('email', user.email),
        Claim('nameidentifier', user.id),
        claim
    )

    await store.add_claims(user_1, claim)

    claims = await store.get_claims(user)
    assert len(claims) == 4

    await store.replace_claim(
        user,
        Claim('name', user.username),
        Claim('phone', '999999999')
    )
    claims = await store.get_claims(user)
    assert len(claims) == 4
    assert any([True for c in claims if c.type == 'phone'])

    await store.remove_claims(user, Claim('phone', '999999999'))
    claims = await store.get_claims(user)
    assert len(claims) == 3

    users = await store.get_users_for_claim(claim)
    assert len(users) == 2
