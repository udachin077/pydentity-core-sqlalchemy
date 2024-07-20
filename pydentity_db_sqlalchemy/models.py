import datetime
from typing import Optional, TYPE_CHECKING, List
from uuid import uuid4

import sqlalchemy as sa
from pydentity.types import TKey, GUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr

__all__ = (
    'Model',
    'IdentityUser',
    'IdentityRole',
    'IdentityUserRole',
    'IdentityUserClaim',
    'IdentityUserLogin',
    'IdentityUserToken',
    'IdentityRoleClaim',
)


class Model(AsyncAttrs, DeclarativeBase):
    __table_args__ = {'extend_existing': True}


class AbstractIdentityUser(Model):
    __tablename__ = 'pydentity_identity_users'
    __abstract__ = True

    if TYPE_CHECKING:
        access_failed_count: int
        concurrency_stamp: Optional[GUID]
        email: Optional[str]
        email_confirmed: bool
        id: TKey
        lockout_enabled: bool
        lockout_end: Optional[datetime.datetime]
        normalized_email: Optional[str]
        normalized_username: Optional[str]
        password_hash: Optional[str]
        phone_number: Optional[str]
        phone_number_confirmed: bool
        security_stamp: Optional[GUID]
        two_factor_enabled: bool
        username: Optional[str]
    else:
        access_failed_count: Mapped[int] = mapped_column(sa.Integer, default=0)
        concurrency_stamp: Mapped[Optional[GUID]] = mapped_column(sa.UUID, nullable=True)
        email: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        email_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        id: Mapped[TKey] = mapped_column(sa.UUID, primary_key=True)
        lockout_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
        lockout_end: Mapped[Optional[datetime.datetime]] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
        normalized_email: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
        normalized_username: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
        password_hash: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        phone_number: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        phone_number_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        security_stamp: Mapped[Optional[GUID]] = mapped_column(sa.UUID, nullable=True)
        two_factor_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        username: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)


class AbstractIdentityRole(Model):
    __tablename__ = 'pydentity_identity_roles'
    __abstract__ = True

    if TYPE_CHECKING:
        concurrency_stamp: Optional[GUID]
        id: TKey
        name: Optional[str]
        normalized_name: Optional[str]
    else:
        concurrency_stamp: Mapped[Optional[GUID]] = mapped_column(sa.UUID, nullable=True)
        id: Mapped[TKey] = mapped_column(sa.UUID, primary_key=True)
        name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        normalized_name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)


class AbstractIdentityUserRole(Model):
    __tablename__ = 'pydentity_identity_user_roles'
    __abstract__ = True

    if TYPE_CHECKING:
        user_id: TKey
        role_id: TKey
    else:
        user_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_users.id', ondelete='CASCADE'),
            primary_key=True
        )
        role_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_roles.id', ondelete='CASCADE'),
            primary_key=True
        )


class AbstractIdentityUserClaim(Model):
    __tablename__ = 'pydentity_identity_user_claims'
    __abstract__ = True

    if TYPE_CHECKING:
        claim_type: Optional[str]
        claim_value: Optional[str]
        user_id: TKey
    else:
        user_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_users.id', ondelete='CASCADE'),
            primary_key=True
        )
        claim_type: Mapped[str] = mapped_column(sa.String(455), primary_key=True)
        claim_value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


class AbstractIdentityUserLogin(Model):
    __tablename__ = 'pydentity_identity_user_logins'
    __abstract__ = True

    if TYPE_CHECKING:
        login_provider: str
        provider_key: str
        provider_display_name: Optional[str]
        user_id: TKey
    else:
        user_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_users.id', ondelete='CASCADE'),
            primary_key=True
        )
        login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
        provider_key: Mapped[str] = mapped_column(sa.String(256))
        provider_display_name: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


class AbstractIdentityUserToken(Model):
    __tablename__ = 'pydentity_identity_user_tokens'
    __abstract__ = True

    if TYPE_CHECKING:
        login_provider: str
        name: str
        value: Optional[str]
        user_id: TKey
    else:
        user_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_users.id', ondelete='CASCADE'),
            primary_key=True
        )
        login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
        name: Mapped[str] = mapped_column(sa.String(256))
        value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


class AbstractIdentityRoleClaim(Model):
    __tablename__ = 'pydentity_identity_role_claims'
    __abstract__ = True

    if TYPE_CHECKING:
        claim_type: Optional[str]
        claim_value: Optional[str]
        role_id: TKey
    else:
        role_id: Mapped[TKey] = mapped_column(
            sa.UUID,
            sa.ForeignKey('pydentity_identity_roles.id', ondelete='CASCADE'),
            primary_key=True
        )
        claim_type: Mapped[str] = mapped_column(sa.String(455), primary_key=True)
        claim_value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


class IdentityUser(AbstractIdentityUser):
    @declared_attr
    def roles(cls) -> Mapped[List['IdentityRole']]:
        return relationship(
            'IdentityRole',
            back_populates='users',
            secondary='pydentity_identity_user_roles'
        )

    @declared_attr
    def claims(cls) -> Mapped[List['IdentityUserClaim']]:
        return relationship('IdentityUserClaim', back_populates='user')

    @declared_attr
    def logins(cls) -> Mapped[List['IdentityUserClaim']]:
        return relationship('IdentityUserLogin', back_populates='user')

    @declared_attr
    def tokens(cls) -> Mapped[List['IdentityUserClaim']]:
        return relationship('IdentityUserToken', back_populates='user')

    def __init__(
            self,
            email: str,
            username: Optional[str] = None,
            **kwargs
    ):
        super().__init__(
            id=uuid4(),
            email=email,
            username=username,
            security_stamp=uuid4(),
            **kwargs
        )

    def __str__(self):
        return self.username or self.email or self.id


class IdentityRole(AbstractIdentityRole):
    @declared_attr
    def users(cls) -> Mapped[List['IdentityUser']]:
        return relationship(
            'IdentityUser',
            back_populates='roles',
            secondary='pydentity_identity_user_roles'
        )

    @declared_attr
    def claims(cls) -> Mapped[List['IdentityRoleClaim']]:
        return relationship('IdentityRoleClaim', back_populates='role')

    def __init__(self, name: str, **kwargs):
        super().__init__(
            id=uuid4(),
            name=name,
            **kwargs
        )

    def __str__(self):
        return self.name or self.id


class IdentityUserRole(AbstractIdentityUserRole):
    pass


class IdentityUserClaim(AbstractIdentityUserClaim):
    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='claims')


class IdentityUserLogin(AbstractIdentityUserLogin):
    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='logins')


class IdentityUserToken(AbstractIdentityUserToken):
    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='tokens')


class IdentityRoleClaim(AbstractIdentityRoleClaim):
    @declared_attr
    def role(self) -> Mapped['IdentityRole']:
        return relationship('IdentityRole', back_populates='claims')


if __name__ == '__main__':
    from sqlalchemy.ext.asyncio import create_async_engine
    import asyncio


    async def main():
        async_engine = create_async_engine("sqlite+aiosqlite:///./test.db")
        async with async_engine.begin() as conn:
            await conn.run_sync(Model.metadata.create_all)


    asyncio.run(main())
