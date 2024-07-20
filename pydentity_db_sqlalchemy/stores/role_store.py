from typing import Type, Generic, Optional
from uuid import uuid4, UUID

from pydentity.abc.stores import IRoleStore, IRoleClaimStore
from pydentity.exc import ArgumentNoneException
from pydentity.identity_result import IdentityResult
from pydentity.security.claims import Claim
from pydentity.types import TRole, TRoleClaim
from sqlalchemy import select, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from pydentity_db_sqlalchemy.models import IdentityRole, IdentityRoleClaim


class RoleStore(IRoleClaimStore[TRole], IRoleStore[TRole], Generic[TRole]):
    role_model: Type[TRole] = IdentityRole
    role_claim_model: Type[TRoleClaim] = IdentityRoleClaim

    def __init__(self, session: AsyncSession):
        self.session = session

    def create_model_from_dict(self, **kwargs):
        return self.role_model(**kwargs)

    async def save_changes(self):
        await self.session.commit()

    async def refresh(self, role: TRole):
        await self.session.refresh(role)

    async def all(self) -> list[TRole]:
        return list((await self.session.scalars(select(self.role_model))).all())

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

        role.concurrency_stamp = uuid4()
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

        role_id = UUID(role_id) if isinstance(role_id, str) else role_id
        statement = select(self.role_model).where(self.role_model.id == role_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def find_by_name(self, normalized_name: str) -> Optional[TRole]:
        if normalized_name is None:
            raise ArgumentNoneException("normalized_name")

        statement = select(self.role_model).where(self.role_model.normalized_name == normalized_name)  # type: ignore
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

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

    async def add_claim(self, role: TRole, claim: Claim) -> None:
        if role is None:
            raise ArgumentNoneException("role")
        if claim is None:
            raise ArgumentNoneException("claim")

        self.session.add(self._create_role_claim(role, claim))
        await self.save_changes()

    async def remove_claim(self, role: TRole, claim: Claim) -> None:
        if role is None:
            raise ArgumentNoneException("role")
        if claim is None:
            raise ArgumentNoneException("claim")

        statement = delete(self.role_claim_model).where(
            and_(
                self.role_claim_model.role_id == role.id,
                self.role_claim_model.claim_type == claim.type,
                self.role_claim_model.claim_value == claim.value
            )
        )
        await self.session.execute(statement)

    async def get_claims(self, role: TRole) -> list[Claim]:
        if role is None:
            raise ArgumentNoneException("role")

        statement = (
            select(self.role_claim_model)
            .where(self.role_claim_model.role_id == user.id)  # type: ignore
        )
        role_claims = (await self.session.scalars(statement)).all()
        return [self._create_claim(uc) for uc in role_claims]

    def _create_claim(self, model: TRoleClaim) -> Claim:  # noqa
        return Claim(
            claim_type=model.claim_type,
            claim_value=model.claim_value,
        )

    def _create_role_claim(self, role: TRole, claim: Claim) -> TRoleClaim:
        return self.role_claim_model(
            role_id=role.id,
            claim_type=claim.type,
            claim_value=claim.value
        )
