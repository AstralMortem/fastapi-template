from project.core.cbv import View
from project.core.security import UserDepends, Authorization, HasRole
from project.models import User
from project.schemas import UserRead, UserCreate, UserUpdate, Page
from project.dependencies import UserServiceDep, PaginationDep, AuthServiceDep
from fastapi import Depends

import uuid


class UserView(View):
    prefix = "/users"
    tags = ["Users"]
    resource = "users"

    auto_guard = True
    service: UserServiceDep
    auth_service: AuthServiceDep

    @View.get("/me", response_model=UserRead)
    async def get_current_user(self, user: User = UserDepends(Authorization())):
        return user

    @View.patch("/me", response_model=UserRead)
    async def update_current_user(
        self, payload: UserUpdate, user: User = UserDepends(Authorization())
    ):
        return await self.auth_service.update(user, UserUpdate, True)

    @View.get("/{user_id}", response_model=UserRead)
    async def get_user(self, user_id: uuid.UUID):
        return await self.service.get(user_id)

    @View.get("/", response_model=Page[UserRead])
    async def get_list_of_users(self, pagination: PaginationDep):
        return await self.service.get_many(pagination)

    @View.post("/", response_model=UserRead)
    async def create_user(self, user: UserCreate):
        return await self.auth_service.signup(user, False)

    @View.patch("/{user_id}", response_model=UserRead)
    async def update_user(self, user_id: uuid.UUID, payload: UserUpdate):
        return await self.service.patch(user_id, payload)

    @View.delete("/{user_id}", response_model=UserRead)
    async def delete_user(self, user_id: uuid.UUID):
        return await self.service.delete(user_id)
