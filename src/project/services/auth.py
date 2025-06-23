import uuid
from project.repositories.auth import IUserRepository
from project.schemas.users import UserCreate, UserUpdate
from .base import GenericService
from project.models import User
from project.config import settings
from project.core.exceptions import BackendException, http_status
from project.utils.password import DefaultPasswordHelper, IPasswordHelper
from project.utils.jwts import to_jwt_payload, to_jwt_token
from project.schemas.auth import TokenResponse, AccessToken
from fastapi import Depends
from typing import Annotated, Any
from project.repositories import UserRepoDep


class AuthService(GenericService[IUserRepository]):
    def __init__(
        self,
        user_repo: IUserRepository,
        password_helper: IPasswordHelper = DefaultPasswordHelper(),
    ):
        super().__init__(user_repo)
        self.password_helper = password_helper

    def not_found_error(self):
        return BackendException(
            http_status.HTTP_401_UNAUTHORIZED,
            "Invalid credentials",
            "User with provided credentials not found",
        )

    def parse_user_id(self, user_id: str) -> Any:
        return uuid.UUID(user_id)

    def _validate_user(self, user: User | None) -> User:
        if user is None:
            raise self.not_found_error()

        if not user.is_active and not settings.ALLOW_INACIVE_USER_LOGIN:
            raise self.not_found_error()

        if not user.is_verified and not settings.ALLOW_UNVERIFIED_USER_LOGIN:
            raise self.not_found_error()

        return user

    def _create_access_token(self, user: User):
        permissions = [
            f"{permission.resource}:{permission.action}"
            for permission in user.role.permissions
        ]

        payload = AccessToken(
            sub=str(user.id),
            email=user.email,
            role=user.role.name,
            permissions=permissions,
            aud=settings.ACCESS_TOKEN_AUDIENCE,
            expires_in=settings.ACCESS_TOKEN_MAX_AGE,
        )

        return to_jwt_token(payload)

    def _user_login_response(self, user: User):
        access_token = self._create_access_token(user)

        return TokenResponse(access_token=access_token)

    def decode_token(self, token: str) -> AccessToken:
        return AccessToken.model_validate(to_jwt_payload(token, audience=settings.ACCESS_TOKEN_AUDIENCE))

    async def get_current_user(self, user_id: str) -> User:
        user = await self.main_repo.get_by_id(self.parse_user_id(user_id))
        return self._validate_user(user)

    async def login(self, username: str, password: str) -> TokenResponse:
        try:
            user = await self.main_repo.get_user_by_login_fields(
                settings.LOGIN_FIELDS, username
            )
        except ValueError as e:
            raise BackendException(
                http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Server error",
                "Invalid login fields",
                e,
            )

        user = self._validate_user(user)

        is_valid, new_hash = self.password_helper.verify_and_update(
            password, user.hashed_password
        )
        if not is_valid:
            raise self.not_found_error()

        if new_hash:
            user = await self.main_repo.update(user, {"hashed_password": new_hash})

        return self._user_login_response(user)

    async def signup(self, payload: UserCreate, safe: bool = True):
        for field in settings.LOGIN_FIELDS:
            if hasattr(payload, field):
                user = await self.main_repo.get_by_field(field, getattr(payload, field))
                if user is not None:
                    raise BackendException(
                        http_status.HTTP_403_FORBIDDEN,
                        "User already exist",
                        "User with provided credentials already exist",
                    )

        payload_dict = payload.model_dump()
        payload_dict["hashed_password"] = self.password_helper.hash(
            payload_dict.pop("password")
        )

        if safe:
            payload_dict["is_active"] = settings.DEFAULT_USER_IS_ACTIVE
            payload_dict["is_verified"] = settings.DEFAULT_USER_IS_VERIFIED
            payload_dict["role_id"] = settings.DEFAULT_USER_ROLE_ID

        user = await self.main_repo.create(payload_dict)

        return user

    async def update(self, instance: User, payload: UserUpdate, safe: bool = True):
        for field in settings.LOGIN_FIELDS:
            if hasattr(payload, field):
                user = await self.main_repo.get_by_field(field, getattr(payload, field))
                if user is not None:
                    raise BackendException(
                        http_status.HTTP_403_FORBIDDEN,
                        "User already exist",
                        f"User with same {field} already exists",
                    )

        payload_dict = payload.model_dump(
            exclude_none=True, exclude_defaults=True, exclude_unset=True
        )

        if safe:
            payload_dict["is_active"] = settings.DEFAULT_USER_IS_ACTIVE
            payload_dict["is_verified"] = settings.DEFAULT_USER_IS_VERIFIED
            payload_dict["role_id"] = settings.DEFAULT_USER_ROLE_ID

        return await self.main_repo.update(instance, payload_dict)


async def get_auth_service(user_repo: UserRepoDep):
    return AuthService(user_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
