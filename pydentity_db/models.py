from typing import List
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship

from pydentity_db.base.abstract import (
    AbstractIdentityRole,
    AbstractIdentityRoleClaim,
    AbstractIdentityUser,
    AbstractIdentityUserClaim,
    AbstractIdentityUserLogin,
    AbstractIdentityUserRole,
    AbstractIdentityUserToken,
)
from pydentity_db.base.model import Model

__all__ = (
    'IdentityRole',
    'IdentityRoleClaim',
    'IdentityUser',
    'IdentityUserClaim',
    'IdentityUserLogin',
    'IdentityUserRole',
    'IdentityUserToken',
    'Model',
)


class IdentityUser(AbstractIdentityUser):
    """The default implementation of AbstractIdentityUser which uses a string as a primary key."""

    __personal_data__ = (
        'id',
        'username',
        'email',
        'email_confirmed',
        'phone_number',
        'phone_number_confirmed',
        'two_factor_enabled',
    )

    id: Mapped[str] = mapped_column(sa.String(450))

    @declared_attr
    def roles(cls) -> Mapped[List['IdentityRole']]:
        return relationship('IdentityRole', back_populates='users', secondary='pydentity_user_roles')

    @declared_attr
    def claims(cls) -> Mapped[List['IdentityUserClaim']]:
        return relationship('IdentityUserClaim', back_populates='user')

    @declared_attr
    def logins(cls) -> Mapped[List['IdentityUserLogin']]:
        return relationship('IdentityUserLogin', back_populates='user')

    @declared_attr
    def tokens(cls) -> Mapped[List['IdentityUserToken']]:
        return relationship('IdentityUserToken', back_populates='user')

    def __init__(self, email: str, username: str | None = None, **kwargs) -> None:
        super().__init__(
            id=str(uuid4()),
            email=email,
            username=username,
            security_stamp=str(uuid4()),
            **kwargs
        )


class IdentityRole(AbstractIdentityRole):
    """The default implementation of AbstractIdentityRole which uses a string as the primary key."""

    id: Mapped[str] = mapped_column(sa.String(450))

    @declared_attr
    def users(cls) -> Mapped[List['IdentityUser']]:
        return relationship('IdentityUser', back_populates='roles', secondary='pydentity_user_roles')

    @declared_attr
    def claims(cls) -> Mapped[List['IdentityRoleClaim']]:
        return relationship('IdentityRoleClaim', back_populates='role')

    def __init__(self, name: str, **kwargs) -> None:
        super().__init__(id=str(uuid4()), name=name, **kwargs)


class IdentityUserRole(AbstractIdentityUserRole):
    """Represents the link between a user and a role."""


class IdentityUserClaim(AbstractIdentityUserClaim):
    """Represents a claim that a user possesses."""

    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='claims')


class IdentityUserLogin(AbstractIdentityUserLogin):
    """Represents a login and its associated provider for a user."""

    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='logins')


class IdentityUserToken(AbstractIdentityUserToken):
    """Represents an authentication token for a user."""

    __personal_data__ = ('value',)

    @declared_attr
    def user(self) -> Mapped['IdentityUser']:
        return relationship('IdentityUser', back_populates='tokens')


class IdentityRoleClaim(AbstractIdentityRoleClaim):
    """Represents a claim that is granted to all users within a role."""

    @declared_attr
    def role(self) -> Mapped['IdentityRole']:
        return relationship('IdentityRole', back_populates='claims')
