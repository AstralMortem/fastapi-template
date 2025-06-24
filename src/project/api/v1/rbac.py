from project.core.cbv import View
from project.dependencies import RoleServiceDep, PermissionServiceDep, PaginationDep
from project.schemas import (
    RoleRead,
    Page,
    RoleCreate,
    RoleUpdate,
    PermissionCreate,
    PermissionRead,
    PermissionUpdate,
)


class RoleView(View):
    prefix = "/roles"
    tags = ["RBAC"]
    resource = 'roles'

    auto_guard = True
    service: RoleServiceDep

    @View.get("/{role_id}", response_model=RoleRead)
    async def get_role(self, role_id: int):
        return await self.service.get(role_id)

    @View.get("/", response_model=Page[RoleRead])
    async def get_list_of_roles(self, pagination: PaginationDep):
        return await self.service.get_many(pagination)

    @View.post("/", response_model=RoleRead)
    async def create_role(self, role: RoleCreate):
        return await self.service.create(role)

    @View.patch("/{role_id}", response_model=RoleRead)
    async def update_role(self, role_id: int, role: RoleUpdate):
        return await self.service.patch(role_id, role)

    @View.delete("/{role_id}", response_model=RoleRead)
    async def delete_role(self, role_id: int):
        return await self.service.delete(role_id)


class PermissionView(View):
    prefix = "/permissions"
    tags = ["RBAC"]
    resource = 'permissions'

    auto_guard = True
    service: PermissionServiceDep

    @View.get("/{permission_id}", response_model=PermissionRead)
    async def get_permission(self, permission_id: int):
        return await self.service.get(permission_id)

    @View.get("/", response_model=Page[PermissionRead])
    async def get_list_of_permissions(self, pagination: PaginationDep):
        return await self.service.get_many(pagination)

    @View.post("/", response_model=PermissionRead)
    async def create_permission(self, permission: PermissionCreate):
        return await self.service.create(permission)

    @View.patch("/{permission_id}", response_model=PermissionRead)
    async def update_permission(self, permission_id: int, permission: PermissionUpdate):
        return await self.service.patch(permission_id, permission)

    @View.delete("/{permission_id}", response_model=PermissionRead)
    async def delete_permission(self, permission_id: int):
        return await self.service.delete(permission_id)
