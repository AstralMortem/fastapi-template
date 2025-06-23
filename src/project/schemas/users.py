from .base import ReadSchema, CreateSchema, UpdateSchema
from .rbac import RoleRead
import uuid


class UserRead(ReadSchema):
    id: uuid.UUID
    email: str
    is_active: bool
    is_verified: bool

    role: RoleRead


class UserCreate(CreateSchema):
    email: str
    password: str
    is_active: bool
    is_verified: bool
    role_id: int


class UserUpdate(UpdateSchema):
    email: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    role_id: int | None = None
