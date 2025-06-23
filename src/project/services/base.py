from project.repositories.base import IRepository, M, ID
from project.core.exceptions import BackendException, http_status
from project.schemas.base import UpdateSchema, CreateSchema
from typing import Any, Generic, TypeVar
from fastapi_pagination.bases import AbstractPage, AbstractParams
from fastapi_filter.base.filter import BaseFilterModel
from fastapi import Request

REPO = TypeVar("REPO", bound=IRepository)
CS = TypeVar("CS", bound=CreateSchema)
US = TypeVar("US", bound=UpdateSchema)


class GenericService(Generic[REPO, M, ID]):
    def __init__(self, repository: REPO):
        self.main_repo = repository

    async def get(self, id: ID, **kwargs) -> M:
        instance = await self.main_repo.get_by_id(id, **kwargs)
        if instance is None:
            raise self.not_found_error()
        return instance


    def not_found_error(self):
        return BackendException(
            http_status.HTTP_404_NOT_FOUND,
            "Resource Not Found",
            f"{self.main_repo.model.__name__} not found",
        )


class BaseReadService(Generic[REPO, M, ID], GenericService[REPO, M, ID]):

    async def get_many(
        self,
        pagination: AbstractParams,
        filter: BaseFilterModel | None = None,
        **kwargs,
    ) -> AbstractPage[M]:
        return await self.main_repo.get_many(pagination, filter, **kwargs)


class BaseCreateService(Generic[REPO, M, ID, CS], GenericService[REPO, M, ID]):
    async def create(self, payload: CS, **kwargs) -> M:
        request = kwargs.get("request", None)
        payload_dict = payload.model_dump()

        await self.on_before_create(payload_dict, request)
        instance = await self.main_repo.create(payload_dict, **kwargs)
        await self.on_after_create(instance, payload_dict, request)

        return instance

    async def on_before_create(
        self, payload: dict[str, Any], request: Request | None = None, **kwargs
    ):
        """
        On before create hook
        """

    async def on_after_create(
        self,
        instance: M,
        payload: dict[str, Any],
        request: Request | None = None,
        **kwargs,
    ):
        """
        On after create hook
        """


class BaseUpdateService(Generic[REPO, M, ID, US], GenericService[REPO, M, ID]):

    async def _update(self, instance: M, payload: dict[str, Any], **kwargs) -> M:
        request = kwargs.get("request", None)
        await self.on_before_update(instance, payload, request)
        instance = await self.main_repo.update(instance, payload, **kwargs)
        await self.on_after_update(instance, payload, request)
        return instance

    async def patch(self, id: ID, payload: US, **kwargs) -> M:
        instance = await self.get(id, **kwargs)
        payload_dict = payload.model_dump(
            exclude_unset=True, exclude_defaults=True, exclude_none=True
        )
        return await self._update(instance, payload_dict, **kwargs)

    async def put(self, id: ID, payload: US, **kwargs) -> M:
        instance = await self.get(id, **kwargs)
        payload_dict = payload.model_dump(exclude_defaults=True)
        return await self._update(instance, payload_dict, **kwargs)

    async def on_before_update(
        self,
        instance: M,
        payload: dict[str, Any],
        request: Request | None = None,
        **kwargs,
    ):
        """
        On before update hook
        """

    async def on_after_update(
        self,
        instance: M,
        payload: dict[str, Any],
        request: Request | None = None,
        **kwargs,
    ):
        """
        On after update hook
        """


class BaseDeleteService(Generic[REPO, M, ID], GenericService[REPO, M, ID]):
    async def delete(self, id: ID, **kwargs) -> M:
        request = kwargs.get("request", None)
        instance = await self.get(id, **kwargs)
        await self.on_before_delete(instance, request, **kwargs)
        await self.main_repo.delete(instance, **kwargs)
        await self.on_after_delete(instance, request, **kwargs)
        return instance

    async def on_before_delete(
        self, instance: M, request: Request | None = None, **kwargs
    ):
        """
        On before delete hook
        """

    async def on_after_delete(
        self, instance: M, request: Request | None = None, **kwargs
    ):
        """
        On after delete hook
        """


class BaseCRUDService(
    Generic[REPO, M, ID, CS, US],
    BaseReadService[REPO, M, ID],
    BaseCreateService[REPO, M, ID, CS],
    BaseUpdateService[REPO, M, ID, US],
    BaseDeleteService[REPO, M, ID],
):
    pass
