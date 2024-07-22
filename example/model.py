"""
    CREATE TABLE pydentity_users (
        first_name VARCHAR(256),
        last_name VARCHAR(256),
        ...
    )

    CREATE TABLE orders (
        id INTEGER NOT NULL,
        number VARCHAR(100) NOT NULL,
        user_id VARCHAR(450),
        PRIMARY KEY (id)
)
"""
import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import mapped_column, Mapped

from pydentity_db_sqlalchemy.models import Model, IdentityUser


class CustomUser(IdentityUser):
    first_name: Mapped[str] = mapped_column(sa.String(256))
    last_name: Mapped[str] = mapped_column(sa.String(256))


class Order(Model):
    __tablename__ = 'orders'

    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(sa.String(100))
    user_id = mapped_column(sa.ForeignKey('pydentity_users.id', ondelete='CASCADE'))


async def main():
    async_engine = create_async_engine("sqlite+aiosqlite://", echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(main())
