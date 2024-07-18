from typing import Type, Generic, Optional
from uuid import uuid4

from pydentity.abc.stores import IRoleStore
from pydentity.exc import ArgumentNoneException
from pydentity.identity_result import IdentityResult
from pydentity.types import TRole
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pydentity_db_sqlalchemy.models import IdentityRole


class RoleStore(IRoleStore[TRole], Generic[TRole]):
    role_model: Type[TRole] = IdentityRole

    def __init__(self, session: AsyncSession):
        self.session = session

    def create_model_from_dict(self, **kwargs):
        return self.role_model(**kwargs)

    async def save_changes(self):
        await self.session.commit()

    async def refresh(self, role):
        await self.session.refresh(role)

    async def all(self) -> list[TRole]:
        statement = select(self.role_model)
        return list((await self.session.scalars(statement)).all())

    async def create(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneException("role")

        self.session.add(role)
        await self.save_changes()
        await self.refresh(role)
        return IdentityResult.success()

    async def update(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneException("role")

        role.concurrency_stamp = str(uuid4())
        await self.save_changes()
        await self.refresh(role)
        return IdentityResult.success()

    async def delete(self, role: TRole) -> IdentityResult:
        if role is None:
            raise ArgumentNoneException("role")

        await self.session.delete(role)
        await self.save_changes()
        return IdentityResult.success()

    async def find_by_id(self, role_id: str) -> Optional[TRole]:
        if role_id is None:
            raise ArgumentNoneException("role_id")

        statement = select(self.role_model).where(self.role_model.id == role_id)
        return await self._find_role(statement)

    async def find_by_name(self, normalized_name: str) -> Optional[TRole]:
        if normalized_name is None:
            raise ArgumentNoneException("normalized_name")

        statement = select(self.role_model).where(self.role_model.normalized_name == normalized_name)  # type: ignore
        return await self._find_role(statement)

    async def get_role_id(self, role: TRole) -> str:
        if role is None:
            raise ArgumentNoneException("role")

        return str(role.id)

    async def get_role_name(self, role: TRole) -> Optional[str]:
        if role is None:
            raise ArgumentNoneException("role")

        return role.name

    async def set_role_name(self, role: TRole, role_name: Optional[str]) -> None:
        if role is None:
            raise ArgumentNoneException("role")

        role.name = role_name

    async def get_normalized_role_name(self, role: TRole) -> Optional[str]:
        if role is None:
            raise ArgumentNoneException("role")

        return role.normalized_name

    async def set_normalized_role_name(self, role: TRole, normalized_name: Optional[str]) -> None:
        if role is None:
            raise ArgumentNoneException("role")

        role.normalized_name = normalized_name

    async def _find_role(self, statement) -> Optional[TRole]:
        return (await self.session.execute(statement)).scalar_one_or_none()
