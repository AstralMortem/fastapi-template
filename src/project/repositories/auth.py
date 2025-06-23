from .base import IRepository, BaseRepository
from project.models import User
from project.core.session import SessionDep
from typing import Annotated, Any
from fastapi import Depends
from sqlalchemy import select, or_
import uuid


class IUserRepository(IRepository[User, uuid.UUID]):
    model = User

    async def get_user_by_login_fields(
        self, login_fields: list[str], value: Any
    ) -> User | None:
        raise NotImplementedError


class UserRepository(IUserRepository, BaseRepository[User, uuid.UUID]):
    async def get_user_by_login_fields(self, login_fields, value):
        for field in login_fields:
            if not hasattr(self.model, field):
                raise ValueError(
                    f"Field '{field}' does not exist on model '{self.model.__name__}'"
                )

        qs = (
            select(self.model)
            .where(
                or_(*[getattr(self.model, field) == value for field in login_fields])
            )
            .limit(1)
        )
        return await self.session.scalar(qs)


async def get_user_repository(session: SessionDep):
    return UserRepository(session)


UserRepoDep = Annotated[IUserRepository, Depends(get_user_repository)]
