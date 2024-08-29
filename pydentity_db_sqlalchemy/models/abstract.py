from datetime import datetime
from typing import Optional, TYPE_CHECKING

import sqlalchemy as sa
from pydentity.types import TKey, GUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from pydentity_db_sqlalchemy.types import ProtectedPersonalDataField

__all__ = (
    'Model',
    'AbstractIdentityUser',
    'AbstractIdentityRole',
    'AbstractIdentityUserRole',
    'AbstractIdentityUserClaim',
    'AbstractIdentityRoleClaim',
    'AbstractIdentityUserToken',
    'AbstractIdentityUserLogin'
)

MAX_KEY_LENGTH = 128


class Model(AsyncAttrs, DeclarativeBase):
    pass


class AbstractIdentityUser(Model):
    __tablename__ = 'pydentity_users'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        {'extend_existing': True}
    )
    __abstract__ = True

    if TYPE_CHECKING:
        access_failed_count: int
        concurrency_stamp: Optional[GUID]
        email: Optional[str]
        email_confirmed: bool
        id: TKey
        lockout_enabled: bool
        lockout_end: Optional[datetime]
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
        concurrency_stamp: Mapped[Optional[GUID]] = mapped_column(sa.Text, nullable=True)
        email: Mapped[Optional[str]] = mapped_column(ProtectedPersonalDataField(256), nullable=True)
        email_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        lockout_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
        lockout_end: Mapped[Optional[datetime]] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
        normalized_email: Mapped[Optional[str]] = mapped_column(ProtectedPersonalDataField(256), nullable=True)
        normalized_username: Mapped[Optional[str]] = mapped_column(ProtectedPersonalDataField(256), nullable=True)
        password_hash: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        phone_number: Mapped[Optional[str]] = mapped_column(ProtectedPersonalDataField(256), nullable=True)
        phone_number_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        security_stamp: Mapped[Optional[GUID]] = mapped_column(sa.Text, nullable=True)
        two_factor_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        username: Mapped[Optional[str]] = mapped_column(ProtectedPersonalDataField(256), nullable=True)


class AbstractIdentityRole(Model):
    __tablename__ = 'pydentity_roles'
    __table_args__ = (
        sa.PrimaryKeyConstraint('id'),
        {'extend_existing': True}
    )
    __abstract__ = True

    if TYPE_CHECKING:
        concurrency_stamp: Optional[GUID]
        id: TKey
        name: Optional[str]
        normalized_name: Optional[str]
    else:
        concurrency_stamp: Mapped[Optional[GUID]] = mapped_column(sa.Text, nullable=True)
        name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        normalized_name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)


class AbstractIdentityUserRole(Model):
    __tablename__ = 'pydentity_user_roles'
    __table_args__ = (
        sa.PrimaryKeyConstraint('user_id', 'role_id'),
        {'extend_existing': True}
    )

    if TYPE_CHECKING:
        user_id: TKey
        role_id: TKey
    else:
        user_id = mapped_column(sa.ForeignKey('pydentity_users.id', ondelete='CASCADE'))
        role_id = mapped_column(sa.ForeignKey('pydentity_roles.id', ondelete='CASCADE'))


class AbstractIdentityUserClaim(Model):
    __tablename__ = 'pydentity_user_claims'
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        claim_type: Optional[str]
        claim_value: Optional[str]
        user_id: TKey
    else:
        id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
        claim_type: Mapped[str] = mapped_column(sa.Text, nullable=True)
        claim_value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        user_id = mapped_column(sa.ForeignKey('pydentity_users.id', ondelete='CASCADE'))


class AbstractIdentityUserLogin(Model):
    __tablename__ = 'pydentity_user_logins'
    __table_args__ = (
        sa.PrimaryKeyConstraint('login_provider', 'provider_key'),
        {'extend_existing': True}
    )

    if TYPE_CHECKING:
        login_provider: str
        provider_key: str
        provider_display_name: Optional[str]
        user_id: TKey
    else:
        login_provider: Mapped[str] = mapped_column(sa.String(128))
        provider_key: Mapped[str] = mapped_column(sa.String(128))
        provider_display_name: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        user_id = mapped_column(sa.ForeignKey('pydentity_users.id', ondelete='CASCADE'))


class AbstractIdentityUserToken(Model):
    __tablename__ = 'pydentity_user_tokens'
    __table_args__ = (
        sa.PrimaryKeyConstraint('user_id', 'login_provider', 'name'),
        {'extend_existing': True}
    )

    if TYPE_CHECKING:
        login_provider: str
        name: str
        value: Optional[str]
        user_id: TKey
    else:
        user_id = mapped_column(sa.ForeignKey('pydentity_users.id', ondelete='CASCADE'))
        login_provider: Mapped[str] = mapped_column(sa.String(MAX_KEY_LENGTH))
        name: Mapped[str] = mapped_column(sa.String(MAX_KEY_LENGTH))
        value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)


class AbstractIdentityRoleClaim(Model):
    __tablename__ = 'pydentity_role_claims'
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        id: int
        claim_type: Optional[str]
        claim_value: Optional[str]
        role_id: TKey
    else:
        id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
        claim_type: Mapped[str] = mapped_column(sa.String(455))
        claim_value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        role_id = mapped_column(sa.ForeignKey('pydentity_roles.id', ondelete='CASCADE'))
