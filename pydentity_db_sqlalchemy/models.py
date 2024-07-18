import datetime
import uuid
from typing import Optional, TYPE_CHECKING, List

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from pydentity.types import TKey, GUID


class DbModel(AsyncAttrs, DeclarativeBase):

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({','.join(
            f"{k}={v!r}" for k, v in self.__dict__.items()
            if not k.startswith(('_', '__',))
        )})"


class IdentityUser(DbModel):
    __tablename__ = "identity_users"
    __table_args__ = {'extend_existing': True}

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
        access_failed_count: Mapped[int] = mapped_column(sa.Boolean, default=0)
        concurrency_stamp: Mapped[Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
        email: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        email_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        id: Mapped[uuid.UUID] = mapped_column(sa.String(36), primary_key=True)
        lockout_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=True)
        lockout_end: Mapped[Optional[datetime.datetime]] = mapped_column(sa.TIMESTAMP(timezone=True), nullable=True)
        normalized_email: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
        normalized_username: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)
        password_hash: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        phone_number: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        phone_number_confirmed: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        security_stamp: Mapped[Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
        two_factor_enabled: Mapped[bool] = mapped_column(sa.Boolean, default=False)
        username: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)

        roles: Mapped[List['IdentityRole']] = relationship(
            "IdentityRole", secondary="identity_user_roles", back_populates="users"
        )
        claims: Mapped[List['IdentityUserClaim']] = relationship("IdentityUserClaim", back_populates="user")
        logins: Mapped[List['IdentityUserLogin']] = relationship("IdentityUserLogin", back_populates="user")
        tokens: Mapped[List['IdentityUserToken']] = relationship("IdentityUserToken", back_populates="user")

        def __init__(
                self,
                username: str = None,
                email: str = None,
                phone_number: str = None,
                lockout_enabled: bool = True,
                two_factor_enabled: bool = False,
                **kwargs
        ):
            super().__init__(
                id=str(uuid.uuid4()),
                security_stamp=str(uuid.uuid4()),
                username=username,
                email=email,
                lockout_enabled=lockout_enabled,
                phone_number=phone_number,
                two_factor_enabled=two_factor_enabled,
                **kwargs
            )

        def __str__(self):
            return self.username or self.email or self.id


class IdentityRole(DbModel):
    __tablename__ = "identity_roles"
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        concurrency_stamp: Optional[GUID]
        id: TKey
        name: Optional[str]
        normalized_name: Optional[str]
    else:
        concurrency_stamp: Mapped[Optional[uuid.UUID]] = mapped_column(sa.String(36), nullable=True)
        id: Mapped[uuid.UUID] = mapped_column(sa.String(36), primary_key=True)
        name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True)
        normalized_name: Mapped[Optional[str]] = mapped_column(sa.String(256), nullable=True, unique=True)

        users: Mapped[List['IdentityUser']] = relationship(
            "IdentityUser", secondary="identity_user_roles", back_populates="roles"
        )

        def __init__(self, name: str = None, **kwargs):
            super().__init__(
                id=str(uuid.uuid4()),
                name=name,
                **kwargs
            )

        def __str__(self):
            return self.name or self.id


class IdentityUserRole(DbModel):
    __tablename__ = "identity_user_roles"
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        user_id: TKey
        role_id: TKey
    else:
        user_id = sa.Column(sa.String(36), sa.ForeignKey(
            "identity_users.id", ondelete="CASCADE"), primary_key=True
                            )
        role_id = sa.Column(sa.String(36), sa.ForeignKey(
            "identity_roles.id", ondelete="CASCADE"), primary_key=True
                            )


class IdentityUserClaim(DbModel):
    __tablename__ = "identity_user_claims"
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        claim_type: Optional[str]
        claim_value: Optional[str]
        user_id: TKey
    else:
        claim_type: Mapped[Optional[str]] = mapped_column(sa.String(455), primary_key=True)
        claim_value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        user_id: Mapped[uuid.UUID] = mapped_column(
            sa.ForeignKey("identity_users.id", ondelete="CASCADE"),
            primary_key=True
        )

        user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="claims")


class IdentityUserLogin(DbModel):
    __tablename__ = "identity_user_logins"
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        login_provider: str
        provider_key: str
        provider_display_name: Optional[str]
        user_id: TKey
    else:
        login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
        provider_key: Mapped[str] = mapped_column(sa.String(256))
        provider_display_name: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey(
            "identity_users.id", ondelete="CASCADE"),
            primary_key=True
        )

        user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="logins")


class IdentityUserToken(DbModel):
    __tablename__ = "identity_user_tokens"
    __table_args__ = {'extend_existing': True}

    if TYPE_CHECKING:
        login_provider: str
        name: str
        value: Optional[str]
        user_id: TKey
    else:
        login_provider: Mapped[str] = mapped_column(sa.String(256), primary_key=True)
        name: Mapped[str] = mapped_column(sa.String(256))
        value: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
        user_id: Mapped[uuid.UUID] = mapped_column(
            sa.ForeignKey("identity_users.id", ondelete="CASCADE"),
            primary_key=True
        )

        user: Mapped['IdentityUser'] = relationship("IdentityUser", back_populates="tokens")
