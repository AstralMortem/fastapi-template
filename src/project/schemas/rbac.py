from .base import ReadSchema, CreateSchema, UpdateSchema


class PermissionRead(ReadSchema):
    id: int
    action: str
    resource: str


class PermissionCreate(CreateSchema):
    action: str
    resource: str


class PermissionUpdate(UpdateSchema):
    action: str | None = None
    resource: str | None = None


class RoleRead(ReadSchema):
    id: int
    name: str
    permissions: list[PermissionRead]


class RoleCreate(CreateSchema):
    name: str


class RoleUpdate(UpdateSchema):
    name: str | None = None
