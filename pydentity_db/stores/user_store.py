from datetime import datetime, UTC
from typing import Type, Generic, Final, Optional, Any
from uuid import uuid4

from pydentity import IdentityResult, UserLoginInfo
from pydentity.exc import ArgumentNoneException, InvalidOperationException
from pydentity.interfaces.stores import (
    IUserAuthenticationTokenStore,
    IUserAuthenticatorKeyStore,
    IUserClaimStore,
    IUserEmailStore,
    IUserLockoutStore,
    IUserLoginStore,
    IUserPasswordStore,
    IUserPhoneNumberStore,
    IUserPersonalDataStore,
    IUserRoleStore,
    IUserSecurityStampStore,
    IUserStore,
    IUserTwoFactorRecoveryCodeStore,
    IUserTwoFactorStore,
)
from pydentity.resources import Resources
from pydentity.security.claims import Claim
from pydentity.types import (
    TRole,
    TUser,
    TUserClaim,
    TUserLogin,
    TUserRole,
    TUserToken,
)
from sqlalchemy import select, delete, insert, update, and_
from sqlalchemy.ext.asyncio import AsyncSession

from pydentity_db.models import (
    IdentityRole,
    IdentityUser,
    IdentityUserClaim,
    IdentityUserLogin,
    IdentityUserRole,
    IdentityUserToken,
)

__all__ = ("UserStore", "PersonalDataError",)


class PersonalDataError(Exception):
    pass


class UserStore(
    IUserAuthenticationTokenStore[TUser],
    IUserAuthenticatorKeyStore[TUser],
    IUserClaimStore[TUser],
    IUserEmailStore[TUser],
    IUserLockoutStore[TUser],
    IUserLoginStore[TUser],
    IUserPasswordStore[TUser],
    IUserPersonalDataStore[TUser],
    IUserPhoneNumberStore[TUser],
    IUserRoleStore[TUser],
    IUserSecurityStampStore[TUser],
    IUserTwoFactorRecoveryCodeStore[TUser],
    IUserTwoFactorStore[TUser],
    IUserStore[TUser],
    Generic[TUser]
):
    user_model: Type[TUser] = IdentityUser
    role_model: Type[TRole] = IdentityRole
    user_role_model: Type[TUserRole] = IdentityUserRole
    user_claim_model: Type[TUserClaim] = IdentityUserClaim
    user_login_model: Type[TUserLogin] = IdentityUserLogin
    user_token_model: Type[TUserToken] = IdentityUserToken

    INTERNAL_LOGIN_PROVIDER: Final[str] = "[Pydentity:UserStore]"
    AUTHENTICATOR_KEY_TOKEN_NAME: Final[str] = "[Pydentity:AuthenticatorKey]"
    RECOVERY_CODE_TOKEN_NAME: Final[str] = "[Pydentity:RecoveryCodes]"

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    def create_model_from_dict(self, **kwargs) -> TUser:
        return self.user_model(**kwargs)  # noqa

    async def save_changes(self) -> None:
        await self.session.commit()

    async def refresh(self, user: TUser) -> None:
        await self.session.refresh(user)

    async def all(self) -> list[TUser]:
        return list((await self.session.scalars(select(self.user_model))).all())

    async def create(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneException('user')

        self.session.add(user)
        await self.save_changes()
        await self.refresh(user)
        return IdentityResult.success()

    async def update(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneException('user')

        user.concurrency_stamp = str(uuid4())
        await self.save_changes()
        await self.refresh(user)
        return IdentityResult.success()

    async def delete(self, user: TUser) -> IdentityResult:
        if user is None:
            raise ArgumentNoneException('user')

        await self.session.delete(user)
        await self.save_changes()
        return IdentityResult.success()

    async def find_by_id(self, user_id: str) -> Optional[TUser]:
        if user_id is None:
            raise ArgumentNoneException('user_id')

        return await self._find_user(select(self.user_model).where(self.user_model.id == user_id))

    # noinspection PyTypeChecker
    async def find_by_name(self, normalized_username: str) -> Optional[TUser]:
        if normalized_username is None:
            raise ArgumentNoneException('normalized_username')

        return await self._find_user(
            select(self.user_model).where(self.user_model.normalized_username == normalized_username)
        )

    async def get_user_id(self, user: TUser) -> str:
        if user is None:
            raise ArgumentNoneException('user')

        return str(user.id)

    async def get_username(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.username

    async def set_username(self, user: TUser, username: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.username = username

    async def get_normalized_username(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.normalized_username

    async def set_normalized_username(self, user: TUser, normalized_name: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.normalized_username = normalized_name

    # noinspection PyTypeChecker
    async def find_by_email(self, normalized_email: str) -> Optional[TUser]:
        if normalized_email is None:
            raise ArgumentNoneException('normalized_email')

        return await self._find_user(
            select(self.user_model).where(self.user_model.normalized_email == normalized_email)
        )

    async def get_email(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.email

    async def set_email(self, user: TUser, email: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.email = email

    async def get_email_confirmed(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneException('user')

        return user.email and user.email_confirmed

    async def get_normalized_email(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.normalized_email

    async def set_normalized_email(self, user: TUser, normalized_email: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.normalized_email = normalized_email

    async def set_email_confirmed(self, user: TUser, confirmed: bool) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.email_confirmed = confirmed

    async def get_password_hash(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.password_hash

    async def has_password(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneException('user')

        return bool(user.password_hash)

    async def set_password_hash(self, user: TUser, password_hash: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.password_hash = password_hash

    async def get_phone_number(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return user.phone_number

    async def set_phone_number(self, user: TUser, phone_number: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.phone_number = phone_number

    async def get_phone_number_confirmed(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneException('user')

        return user.phone_number and user.phone_number_confirmed

    async def set_phone_number_confirmed(self, user: TUser, confirmed: bool) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.phone_number_confirmed = confirmed

    async def get_access_failed_count(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneException('user')

        return user.access_failed_count

    async def get_lockout_enabled(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneException('user')

        return user.lockout_enabled

    async def get_lockout_end_date(self, user: TUser) -> Optional[datetime]:
        if user is None:
            raise ArgumentNoneException('user')

        lockout_end = user.lockout_end
        return lockout_end.astimezone(UTC) if lockout_end else lockout_end

    async def increment_access_failed_count(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneException('user')

        user.access_failed_count += 1
        return user.access_failed_count

    async def reset_access_failed_count(self, user: TUser) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.access_failed_count = 0

    async def set_lockout_enabled(self, user: TUser, enabled: bool) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.lockout_enabled = enabled

    async def set_lockout_end_date(self, user: TUser, lockout_end: Optional[datetime]) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.lockout_end = lockout_end

    async def get_security_stamp(self, user: TUser) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')

        return str(user.security_stamp) if user.security_stamp else None

    async def set_security_stamp(self, user: TUser, stamp: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not stamp:
            raise ArgumentNoneException('stamp')

        user.security_stamp = stamp

    async def add_to_role(self, user: TUser, normalized_role_name: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not normalized_role_name:
            raise ArgumentNoneException('normalized_role_name')

        if role := await self._find_role(normalized_role_name):
            await self.session.execute(insert(self.user_role_model).values(user_id=user.id, role_id=role.id))
            return

        raise InvalidOperationException(Resources.RoleNotFound(normalized_role_name))

    async def get_roles(self, user: TUser) -> list[str]:
        if user is None:
            raise ArgumentNoneException('user')

        query = select(self.role_model.name).where(
            and_(
                self.user_model.id == user.id,
                self.user_model.id == self.user_role_model.user_id,
                self.role_model.id == self.user_role_model.role_id
            )
        )
        roles = await self.session.scalars(query)
        return list(roles.all())

    async def get_users_in_role(self, normalized_role_name: str) -> list[TUser]:
        if not normalized_role_name:
            raise ArgumentNoneException('normalized_role_name')

        if role := await self._find_role(normalized_role_name):
            users: list[TUser] = await role.awaitable_attrs.users
            return users

        raise InvalidOperationException(Resources.RoleNotFound(normalized_role_name))

    async def is_in_role(self, user: TUser, normalized_role_name: str) -> bool:
        if not normalized_role_name:
            raise ArgumentNoneException('normalized_role_name')

        if role := await self._find_role(normalized_role_name):
            query = select(self.user_role_model).where(
                and_(
                    self.user_role_model.user_id == user.id,
                    self.user_role_model.role_id == role.id
                )
            )
            result = await self.session.scalars(query)
            return bool(result.one_or_none())

        return False

    async def remove_from_role(self, user: TUser, normalized_role_name: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not normalized_role_name:
            raise ArgumentNoneException('normalized_role_name')

        if role := await self._find_role(normalized_role_name):
            query = delete(self.user_role_model).where(
                and_(
                    self.user_role_model.user_id == user.id,
                    self.user_role_model.role_id == role.id
                )
            )
            await self.session.execute(query)

    async def add_login(self, user: TUser, login: UserLoginInfo) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if login is None:
            raise ArgumentNoneException('login')

        self.session.add(self._create_user_login(user, login))
        await self.save_changes()

    async def find_by_login(self, login_provider: str, provider_key: str) -> Optional[TUser]:
        if not login_provider:
            raise ArgumentNoneException('login_provider')
        if not provider_key:
            raise ArgumentNoneException('provider_key')

        query = select(self.user_login_model).where(
            and_(
                self.user_login_model.login_provider == login_provider,
                self.user_login_model.provider_key == provider_key
            )
        )

        if user_login := (await self.session.scalars(query)).one_or_none():
            return await self._find_user(select(self.user_model).where(self.user_model.id == user_login.user_id))

    async def get_logins(self, user: TUser) -> list[UserLoginInfo]:
        if user is None:
            raise ArgumentNoneException('user')

        query = select(self.user_login_model).where(self.user_login_model.user_id == user.id)
        user_logins = await self.session.scalars(query)
        return [self._create_user_login_info(ul) for ul in user_logins.all()]

    async def remove_login(self, user: TUser, login_provider: str, provider_key: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not login_provider:
            raise ArgumentNoneException('login_provider')
        if not provider_key:
            raise ArgumentNoneException('provider_key')

        query = delete(self.user_login_model).where(
            and_(
                self.user_login_model.user_id == user.id,
                self.user_login_model.login_provider == login_provider,
                self.user_login_model.provider_key == provider_key
            )
        )
        await self.session.execute(query)

    async def get_token(self, user: TUser, login_provider: str, name: str) -> Optional[str]:
        if user is None:
            raise ArgumentNoneException('user')
        if not login_provider:
            raise ArgumentNoneException('login_provider')
        if not name:
            raise ArgumentNoneException('name')

        if token := await self._find_token(user, login_provider, name):
            return token.value

    async def remove_token(self, user: TUser, login_provider: str, name: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not login_provider:
            raise ArgumentNoneException('login_provider')
        if not name:
            raise ArgumentNoneException('name')

        query = delete(self.user_token_model).where(
            and_(
                self.user_token_model.user_id == user.id,
                self.user_token_model.login_provider == login_provider,
                self.user_token_model.name == name
            )
        )
        await self.session.execute(query)

    async def set_token(self, user: TUser, login_provider: str, name: str, value: Optional[str]) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not login_provider:
            raise ArgumentNoneException('login_provider')
        if not name:
            raise ArgumentNoneException('name')

        if token := await self._find_token(user, login_provider, name):
            token.value = value
            await self.save_changes()
            return

        self.session.add(self._create_user_token(user, login_provider, name, value))
        await self.save_changes()

    async def get_two_factor_enabled(self, user: TUser) -> bool:
        if user is None:
            raise ArgumentNoneException('user')

        return user.two_factor_enabled

    async def set_two_factor_enabled(self, user: TUser, enabled: bool) -> None:
        if user is None:
            raise ArgumentNoneException('user')

        user.two_factor_enabled = enabled

    async def get_authenticator_key(self, user: TUser) -> Optional[str]:
        return await self.get_token(user, self.INTERNAL_LOGIN_PROVIDER, self.AUTHENTICATOR_KEY_TOKEN_NAME)

    async def set_authenticator_key(self, user: TUser, key: str) -> None:
        return await self.set_token(user, self.INTERNAL_LOGIN_PROVIDER, self.AUTHENTICATOR_KEY_TOKEN_NAME, key)

    async def count_codes(self, user: TUser) -> int:
        if user is None:
            raise ArgumentNoneException('user')

        merged_codes = (await self.get_token(user, self.INTERNAL_LOGIN_PROVIDER, self.RECOVERY_CODE_TOKEN_NAME)) or ""

        if merged_codes:
            return merged_codes.count(';') + 1

        return 0

    async def redeem_code(self, user: TUser, code: str) -> bool:
        if user is None:
            raise ArgumentNoneException('user')
        if not code:
            raise ArgumentNoneException('code')

        merged_codes = (await self.get_token(user, self.INTERNAL_LOGIN_PROVIDER, self.RECOVERY_CODE_TOKEN_NAME)) or ""
        split_codes = merged_codes.split(';')

        if code in split_codes:
            split_codes.remove(code)
            await self.replace_codes(user, *split_codes)
            return True

        return False

    async def replace_codes(self, user: TUser, *recovery_codes: str) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not recovery_codes:
            raise ArgumentNoneException('recovery_codes')

        return await self.set_token(
            user,
            self.INTERNAL_LOGIN_PROVIDER,
            self.RECOVERY_CODE_TOKEN_NAME,
            ';'.join(recovery_codes)
        )

    async def add_claims(self, user: TUser, *claims: Claim) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not claims:
            raise ArgumentNoneException('claims')

        self.session.add_all(self._create_user_claim(user, claim) for claim in claims)
        await self.save_changes()

    async def get_claims(self, user: TUser) -> list[Claim]:
        if user is None:
            raise ArgumentNoneException('user')

        query = (
            select(self.user_claim_model)
            .where(self.user_claim_model.user_id == user.id)
        )
        user_claims = (await self.session.scalars(query)).all()
        return [self._create_claim(uc) for uc in user_claims]

    async def get_users_for_claim(self, claim: Claim) -> list[TUser]:
        if claim is None:
            raise ArgumentNoneException('claim')

        query = select(self.user_claim_model).where(
            and_(
                self.user_claim_model.claim_type == claim.type,
                self.user_claim_model.claim_value == claim.value
            )
        )
        user_claims = await self.session.scalars(query)
        return [await uc.awaitable_attrs.user for uc in user_claims.all()]

    async def remove_claims(self, user: TUser, *claims: Claim) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if not claims:
            raise ArgumentNoneException('claims')

        for claim in claims:
            query = select(self.user_claim_model).where(
                and_(
                    self.user_claim_model.user_id == user.id,
                    self.user_claim_model.claim_type == claim.type,
                    self.user_claim_model.claim_value == claim.value
                )
            )

            matches_claims = (await self.session.scalars(query)).all()

            for c in matches_claims:
                await self.session.delete(c)

        await self.save_changes()

    async def replace_claim(self, user: TUser, claim: Claim, new_claim: Claim) -> None:
        if user is None:
            raise ArgumentNoneException('user')
        if claim is None:
            raise ArgumentNoneException('claim')
        if new_claim is None:
            raise ArgumentNoneException('new_claim')

        query = update(self.user_claim_model).where(
            and_(
                self.user_claim_model.user_id == user.id,
                self.user_claim_model.claim_type == claim.type,
                self.user_claim_model.claim_value == claim.value
            )
        ).values(claim_type=new_claim.type, claim_value=new_claim.value)

        await self.session.execute(query)

    async def get_personal_data(self, user: TUser) -> dict[str, Any] | None:
        if hasattr(user, '__personal_data__'):
            return {p: getattr(user, p) for p in getattr(user, '__personal_data__')}

        raise PersonalDataError(
            f"The model '{type(user)}' does not support receiving personal data. "
            f"The model must have the '__personal_data__' attribute, which lists the fields related to personal data."
        )

    def _create_claim(self, model: TUserClaim) -> Claim:  # noqa
        return Claim(
            claim_type=model.claim_type,
            claim_value=model.claim_value,
        )

    def _create_user_claim(self, user: TUser, claim: Claim) -> TUserClaim:
        return self.user_claim_model(
            user_id=user.id,
            claim_type=claim.type,
            claim_value=claim.value
        )

    def _create_user_token(self, user: TUser, login_provider: str, name: str, value: Optional[str]) -> TUserToken:
        return self.user_token_model(
            user_id=user.id,
            login_provider=login_provider,
            name=name,
            value=value
        )

    def _create_user_login_info(self, model: TUserLogin) -> UserLoginInfo:  # noqa
        return UserLoginInfo(
            login_provider=model.login_provider,
            provider_key=model.provider_key,
            display_name=model.provider_display_name
        )

    def _create_user_login(self, user: TUser, login: UserLoginInfo) -> TUserLogin:
        return self.user_login_model(
            user_id=user.id,
            login_provider=login.login_provider,
            provider_display_name=login.display_name,
            provider_key=login.provider_key
        )

    async def _find_token(self, user: TUser, login_provider: str, name: str) -> TUserToken:
        query = select(self.user_token_model).where(
            and_(
                self.user_token_model.user_id == user.id,
                self.user_token_model.login_provider == login_provider,
                self.user_token_model.name == name
            )
        )
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def _find_user(self, query) -> Optional[TUser]:
        result = await self.session.scalars(query)
        return result.one_or_none()

    async def _find_role(self, name: str) -> Optional[TRole]:
        result = await self.session.scalars(
            select(self.role_model)
            .where(self.role_model.normalized_name == name)  # type: ignore
        )
        return result.one_or_none()
