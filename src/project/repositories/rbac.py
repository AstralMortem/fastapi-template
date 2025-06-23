from .base import IRepository, BaseRepository
from project.models import Role, Permission
from project.core.session import SessionDep
from typing import Annotated
from fastapi import Depends
from abc import ABC


class IRoleRepository(IRepository[Role, int], ABC):
    model = Role


class IPermissionRepository(IRepository[Permission, int], ABC):
    model = Permission


class RoleRepository(IRoleRepository, BaseRepository[Role, int]):
    pass


class PermissionRepository(IPermissionRepository, BaseRepository[Permission, int]):
    pass


async def get_role_repository(session: SessionDep):
    return RoleRepository(session)


async def get_permission_repository(session: SessionDep):
    return PermissionRepository(session)


RoleRepoDep = Annotated[IRoleRepository, Depends(get_role_repository)]
PermissionRepoDep = Annotated[IPermissionRepository, Depends(get_permission_repository)]
