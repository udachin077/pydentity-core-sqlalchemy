"""
    CREATE TABLE pydentity_users (
        id VARCHAR(450) NOT NULL,
        access_failed_count INTEGER NOT NULL,
        concurrency_stamp TEXT,
        email VARCHAR(256),
        email_confirmed BOOLEAN NOT NULL,
        lockout_enabled BOOLEAN NOT NULL,
        lockout_end TIMESTAMP,
        normalized_email VARCHAR(256),
        normalized_username VARCHAR(256),
        password_hash TEXT,
        phone_number VARCHAR(256),
        phone_number_confirmed BOOLEAN NOT NULL,
        security_stamp TEXT,
        two_factor_enabled BOOLEAN NOT NULL,
        username VARCHAR(256),
        PRIMARY KEY (id)
    )

    CREATE UNIQUE INDEX "IDX_PYDENTITY_USERS_NORMALIZED_EMAIL" ON pydentity_users (normalized_email)
    CREATE UNIQUE INDEX "IDX_PYDENTITY_USERS_NORMALIZED_USERNAME" ON pydentity_users (normalized_username)

    CREATE TABLE pydentity_roles (
        id VARCHAR(450) NOT NULL,
        concurrency_stamp TEXT,
        name VARCHAR(256),
        normalized_name VARCHAR(256),
        PRIMARY KEY (id)
    )

    CREATE UNIQUE INDEX "IDX_PYDENTITY_ROLES_NORMALIZED_NAME" ON pydentity_roles (normalized_name)

    CREATE TABLE pydentity_user_roles (
        user_id VARCHAR(450) NOT NULL,
        role_id VARCHAR(450) NOT NULL,
        PRIMARY KEY (user_id, role_id),
        FOREIGN KEY(user_id) REFERENCES pydentity_users (id) ON DELETE CASCADE,
        FOREIGN KEY(role_id) REFERENCES pydentity_roles (id) ON DELETE CASCADE
    )

    CREATE TABLE pydentity_user_claims (
        id INTEGER NOT NULL,
        claim_type TEXT,
        claim_value TEXT,
        user_id VARCHAR(450),
        PRIMARY KEY (id),
        FOREIGN KEY(user_id) REFERENCES pydentity_users (id) ON DELETE CASCADE
    )

    CREATE TABLE pydentity_user_logins (
        login_provider VARCHAR(128) NOT NULL,
        provider_key VARCHAR(128) NOT NULL,
        provider_display_name TEXT,
        user_id VARCHAR(450),
        PRIMARY KEY (login_provider, provider_key),
        FOREIGN KEY(user_id) REFERENCES pydentity_users (id) ON DELETE CASCADE
    )

    CREATE TABLE pydentity_user_tokens (
        user_id VARCHAR(450) NOT NULL,
        login_provider VARCHAR(128) NOT NULL,
        name VARCHAR(128) NOT NULL,
        value TEXT,
        PRIMARY KEY (user_id, login_provider, name),
        FOREIGN KEY(user_id) REFERENCES pydentity_users (id) ON DELETE CASCADE
    )

    CREATE TABLE pydentity_role_claims (
        id INTEGER NOT NULL,
        claim_type VARCHAR(455) NOT NULL,
        claim_value TEXT,
        role_id VARCHAR(450),
        PRIMARY KEY (id),
        FOREIGN KEY(role_id) REFERENCES pydentity_roles (id) ON DELETE CASCADE
    )
"""

from typing import Optional, List
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, declared_attr, relationship

from .abstract import (
    Model,
    AbstractIdentityUser,
    AbstractIdentityRole,
    AbstractIdentityUserRole,
    AbstractIdentityUserClaim,
    AbstractIdentityUserLogin,
    AbstractIdentityUserToken,
    AbstractIdentityRoleClaim
)

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


class IdentityUser(AbstractIdentityUser):
    id: Mapped[str] = mapped_column(sa.String(450))

    @declared_attr
    def roles(cls) -> Mapped[List['IdentityRole']]:
        return relationship('IdentityRole', back_populates='users', secondary='pydentity_user_roles')

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
            id=str(uuid4()),
            email=email,
            username=username,
            security_stamp=str(uuid4()),
            **kwargs
        )

    def __str__(self):
        return self.username or self.email or self.id


class IdentityRole(AbstractIdentityRole):
    id: Mapped[str] = mapped_column(sa.String(450))

    @declared_attr
    def users(cls) -> Mapped[List['IdentityUser']]:
        return relationship('IdentityUser', back_populates='roles', secondary='pydentity_user_roles')

    @declared_attr
    def claims(cls) -> Mapped[List['IdentityRoleClaim']]:
        return relationship('IdentityRoleClaim', back_populates='role')

    def __init__(self, name: str, **kwargs):
        super().__init__(
            id=str(uuid4()),
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


sa.Index('IDX_PYDENTITY_USERS_NORMALIZED_EMAIL', IdentityUser.normalized_email, unique=True)
sa.Index('IDX_PYDENTITY_USERS_NORMALIZED_USERNAME', IdentityUser.normalized_username, unique=True)
sa.Index('IDX_PYDENTITY_ROLES_NORMALIZED_NAME', IdentityRole.normalized_name, unique=True)
