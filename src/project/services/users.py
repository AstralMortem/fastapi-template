import uuid
from .base import BaseCRUDService
from project.repositories import UserRepoDep
from project.repositories.auth import IUserRepository
from project.models import User
from project.schemas import UserCreate, UserUpdate
from fastapi import Depends
from typing import Annotated


class UserService(BaseCRUDService[IUserRepository, User, uuid.UUID, UserCreate, UserUpdate]):
    pass


async def get_user_service(user_repo: UserRepoDep):
    return UserService(user_repo)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
