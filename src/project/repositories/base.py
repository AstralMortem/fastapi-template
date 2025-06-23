from typing import TypeVar, Generic, Any
from project.models.base import Model
from abc import ABC, abstractmethod
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_pagination.ext.sqlalchemy import paginate
from fastapi_filter.base.filter import BaseFilterModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

M = TypeVar("M", bound=Model)
ID = TypeVar("ID")


class IRepository(Generic[M, ID], ABC):
    model: type[M]

    @abstractmethod
    async def get_by_id(self, id: ID, **kwargs) -> M | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_field(self, field: str, value: Any, **kwargs) -> M | None:
        raise NotImplementedError

    @abstractmethod
    async def get_many(
        self,
        pagination: AbstractParams,
        filter: BaseFilterModel | None = None,
        **kwargs,
    ) -> AbstractPage[M]:
        raise NotImplementedError

    @abstractmethod
    async def create(self, data: dict[str, Any], **kwargs) -> M:
        raise NotImplementedError

    @abstractmethod
    async def update(self, instance: M, data: dict[str, Any], **kwargs) -> M:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, instance: M, **kwargs) -> None:
        raise NotImplementedError


class BaseRepository(Generic[M, ID], IRepository[M, ID]):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: ID, **kwargs) -> M | None:
        return await self.session.get(self.model, id)

    async def get_by_field(self, field: str, value: Any, **kwargs) -> M | None:
        qs = select(self.model).filter_by(**{field: value}).limit(1)
        return await self.session.scalar(qs)

    async def get_many(
        self,
        pagination: AbstractParams,
        filter: BaseFilterModel | None = None,
        **kwargs,
    ) -> AbstractPage[M]:
        qs = select(self.model)
        if filter:
            qs = filter.filter(qs)
        return await paginate(self.session, qs, pagination) # type: ignore

    async def create(self, data: dict[str, Any], **kwargs) -> M:
        instance = self.model(**data)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: M, data: dict[str, Any], **kwargs) -> M:
        for key, value in data.items():
            setattr(instance, key, value)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, instance: M, **kwargs) -> M:
        await self.session.delete(instance)
        await self.session.commit()
        return instance
