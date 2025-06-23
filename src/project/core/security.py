from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from project.config import settings
from .exceptions import BackendException, http_status
from project.services import AuthServiceDep
from project.schemas.auth import AccessToken
from enum import StrEnum

auth_key = OAuth2PasswordBearer(tokenUrl=settings.LOGIN_URL_ENDPOINT, auto_error=False)


class Action(StrEnum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


class Authorization:
    resource: str | None = None

    async def check(self, token: AccessToken) -> bool:
        return True

    def __or__(self, other: "Authorization"):
        return _OrPermissionCheck(self, other)

    def __and__(self, other: "Authorization"):
        return _AndPermissionCheck(self, other)

    def _verify_tokens(self, *tokens) -> str:
        for token in tokens:
            if token is not None:
                return token
        raise BackendException(
            http_status.HTTP_401_UNAUTHORIZED, "Not authenticated", "Token not set"
        )

    async def __call__(
        self,
        service: AuthServiceDep,
        auth_token: str | None = Depends(auth_key),
    ):
        token = self._verify_tokens(auth_token)
        token = service.decode_token(token)

        if not await self.check(token):
            raise BackendException(http_status.HTTP_403_FORBIDDEN, "Access Denied", "You don`t have access to this resource")
        return token


class _OrPermissionCheck(Authorization):
    def __init__(self, left: Authorization, right: Authorization):
        self.left = left
        self.right = right

    async def check(self, token: AccessToken) -> bool:
        left_result = await self.left.check(token)
        right_result = await self.right.check(token)
        return left_result or right_result


class _AndPermissionCheck(Authorization):
    def __init__(self, left: Authorization, right: Authorization):
        self.left = left
        self.right = right

    async def check(self, token: AccessToken) -> bool:
        left_result = await self.left.check(token)
        right_result = await self.right.check(token)
        return left_result and right_result


class HasRole(Authorization):
    def __init__(self, role: str):
        self.role = role

    async def check(self, token: AccessToken) -> bool:
        return self.role.lower().strip() == token.role.lower().strip()


class HasPermission(Authorization):
    def __init__(self, action: Action | str):
        self.action = action

    async def check(self, token: AccessToken) -> bool:
        return f"{self.resource}:{self.action}" in list(
            map(lambda x: x.lower().strip(), token.permissions)
        )


def to_user(instance: Authorization):
    async def _current_user(
        service: AuthServiceDep, token: AccessToken = Depends(instance)
    ):
        return await service.get_current_user(token.sub)

    return _current_user


def UserDepends(instance: Authorization):
    return Depends(to_user(instance))


__all__ = ["Authorization", "HasRole", "HasPermission", "UserDepends", "Action"]
