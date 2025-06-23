from fastapi import APIRouter
from .auth import AuthView
from .rbac import RoleView, PermissionView
from .users import UserView

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(AuthView.as_router())
v1_router.include_router(RoleView.as_router())
v1_router.include_router(PermissionView.as_router())
v1_router.include_router(UserView.as_router())
