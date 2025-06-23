from .base import BaseCRUDService
from project.repositories.rbac import IRoleRepository, IPermissionRepository
from project.repositories import RoleRepoDep, PermissionRepoDep
from project.models import Role, Permission
from project.schemas.rbac import (
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    PermissionUpdate,
)
from typing import Annotated
from fastapi import Depends


class RoleService(BaseCRUDService[IRoleRepository, Role, int, RoleCreate, RoleUpdate]):
    pass


class PermissionService(
    BaseCRUDService[
        IPermissionRepository, Permission, int, PermissionCreate, PermissionUpdate
    ]
):
    pass


async def get_role_service(role_repo: RoleRepoDep) -> RoleService:
    return RoleService(role_repo)


async def get_permission_service(
    permission_repo: PermissionRepoDep,
) -> PermissionService:
    return PermissionService(permission_repo)


RoleServiceDep = Annotated[RoleService, Depends(get_role_service)]
PermissionServiceDep = Annotated[PermissionService, Depends(get_permission_service)]
