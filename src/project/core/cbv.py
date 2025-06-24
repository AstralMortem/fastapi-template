from fastapi import APIRouter, Depends, Response
from fastapi.datastructures import DefaultPlaceholder
from fastapi.routing import APIRoute
from fastapi.params import Depends as DependsClass
from starlette.routing import BaseRoute
from makefun import with_signature
from typing import (
    Any,
    Callable,
    ClassVar,
    Dict,
    List,
    Sequence,
    Type,
    Union,
    get_type_hints,
    get_origin,
    Annotated,
    get_args,
    Unpack,
    TypedDict,
    NotRequired,
)
import inspect
from project.core.security import Authorization, Action, HasPermission
from fastapi.types import IncEx

from project.schemas.auth import AccessToken


__VIEW_CLASS__ = "__VIEW_CLASS__"
__VIEW_ROUTE__ = "__VIEW_ROUTE__"


class RouterParams(TypedDict):
    tags: NotRequired[List[str]]
    response_model: NotRequired[Any]
    status_code: NotRequired[int]
    dependencies: NotRequired[Sequence[DependsClass]]
    summary: NotRequired[str]
    description: NotRequired[str]
    response_description: NotRequired[str]
    responses: NotRequired[Dict[Union[int, str], Dict[str, Any]]]
    deprecated: NotRequired[bool]
    name: NotRequired[str]
    response_model_include: NotRequired[IncEx]
    response_model_exclude: NotRequired[IncEx]
    response_model_by_alias: NotRequired[bool]
    response_model_exclude_unset: NotRequired[bool]
    response_model_exclude_defaults: NotRequired[bool]
    response_model_exclude_none: NotRequired[bool]
    include_in_schema: NotRequired[bool]
    response_class: NotRequired[Union[Type[Response], DefaultPlaceholder]]
    dependency_overrides_provider: NotRequired[Any]
    callbacks: NotRequired[List[BaseRoute]]
    openapi_extra: NotRequired[Dict[str, Any]]
    generate_unique_id_function: NotRequired[
        Union[Callable[["APIRoute"], str], DefaultPlaceholder]
    ]


class View:
    prefix: ClassVar[str] = ""
    tags: ClassVar[list[str]] = []
    resource: ClassVar[str] = ""

    auto_guard: ClassVar[bool] = False
    guard_map: ClassVar[dict] = {
        "GET": Action.READ,
        "POST": Action.CREATE,
        "PUT": Action.UPDATE,
        "PATCH": Action.UPDATE,
        "DELETE": Action.DELETE,
    }

    @classmethod
    def as_router(cls, **kwargs):
        prefix = cls.prefix
        tags = kwargs.get("tags", cls.tags)

        router = APIRouter(prefix=prefix, tags=tags, **kwargs)
        cls._init_view()
        router = cls._load_routes(router)

        return router

    @classmethod
    def _init_view(cls):
        if getattr(cls, __VIEW_CLASS__, False):
            return

        old_init = cls.__init__
        old_sign = inspect.signature(old_init)
        old_params = list(old_sign.parameters.values())[
            1:
        ]  # remove self from __init__ args
        new_params = [
            x
            for x in old_params
            if x.kind
            not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        ]

        dependencies = []

        for name, hint in get_type_hints(cls, include_extras=True).items():
            if get_origin(hint) is ClassVar:
                continue

            default = getattr(cls, name, inspect._empty)
            if get_origin(hint) is Annotated:
                args = get_args(hint)
                annotated_hint = args[0]
                depends_param = next(
                    (arg for arg in args[1:] if isinstance(arg, DependsClass)), None
                )

                if depends_param:
                    new_params.append(
                        inspect.Parameter(
                            name=name,
                            kind=inspect.Parameter.KEYWORD_ONLY,
                            annotation=annotated_hint,
                            default=depends_param,
                        )
                    )
                dependencies.append(name)
            else:
                new_params.append(
                    inspect.Parameter(
                        name=name,
                        kind=inspect.Parameter.KEYWORD_ONLY,
                        annotation=hint,
                        default=default,
                    )
                )
                dependencies.append(name)

        new_signature = inspect.Signature(new_params)

        def new_init(self: Any, *args: Any, **kwargs: Any) -> None:
            for dep_name in dependencies:
                dep_value = kwargs.pop(dep_name)
                setattr(self, dep_name, dep_value)
            else:
                old_init(self, *args, **kwargs)

        setattr(cls, "__signature__", new_signature)
        setattr(cls, "__init__", new_init)
        setattr(cls, __VIEW_CLASS__, True)

    @classmethod
    def _load_routes(cls, router: APIRouter) -> APIRouter:
        for _, method in inspect.getmembers(cls, inspect.isfunction):
            if getattr(method, __VIEW_ROUTE__, False):
                route = method(cls)

                old_endpoint = route.endpoint
                old_signature = inspect.signature(old_endpoint)
                old_parameters: List[inspect.Parameter] = list(
                    old_signature.parameters.values()
                )
                old_first_parameter = old_parameters[0]
                new_first_parameter = old_first_parameter.replace(default=Depends(cls))
                new_parameters = [new_first_parameter] + [
                    parameter.replace(kind=inspect.Parameter.KEYWORD_ONLY)
                    for parameter in old_parameters[1:]
                ]

                new_signature = old_signature.replace(parameters=new_parameters)
                setattr(route.endpoint, "__signature__", new_signature)
                router.routes.append(route)

        return router

    @classmethod
    def _guard_endpoint(cls, func: Callable, method: str = "GET"):
        old_sig = inspect.signature(func)
        old_params = list(old_sig.parameters.values())
        params_updated = False

        for idx, param in enumerate(old_params):
            if param.annotation is Authorization or (
                isinstance(param.default, DependsClass)
                and isinstance(param.default.dependency, Authorization)
            ):
                authorization_instance = param.default.dependency
                if authorization_instance is not None:
                    authorization_instance.resource = cls.resource
                auth_param = inspect.Parameter(
                    name=param.name,
                    kind=param.kind,
                    annotation=param.annotation,
                    default=Depends(authorization_instance),
                )
                old_params[idx] = auth_param
                params_updated = True
                break

        if not params_updated and cls.auto_guard:
            action = cls.guard_map.get(method, None)
            if action is None:
                raise ValueError(
                    f"You set auth_guard flag for view, but not set default action for {method} method in guard_map attr"
                )

            guardian = HasPermission(action)
            guardian.resource = cls.resource

            old_params.append(
                inspect.Parameter(
                    name="_",
                    annotation=AccessToken,
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    default=Depends(guardian),
                )
            )

        new_signature = old_sig.replace(parameters=old_params)

        @with_signature(new_signature)
        async def new_func(*args, **kwargs):
            kwargs.pop('_', None)
            return await func(*args, **kwargs)
            
        # return with_signature(new_signature)(func)
        new_func.__name__ = func.__name__
        return new_func

    @classmethod
    def get(cls, path: str, **kwargs: Unpack[RouterParams]):
        def wrapper(func):
            def _wrapper(cls: "View"):
                return APIRoute(
                    path=cls.prefix + path,
                    endpoint=cls._guard_endpoint(func, "GET"),
                    methods=["GET"],
                    tags=kwargs.get("tags", cls.tags),
                    **kwargs,  # type: ignore
                )

            setattr(_wrapper, __VIEW_ROUTE__, True)
            return _wrapper

        return wrapper

    @classmethod
    def post(cls, path: str, **kwargs: Unpack[RouterParams]):
        def wrapper(func):
            def _wrapper(cls: "View"):
                return APIRoute(
                    path=cls.prefix + path,
                    endpoint=cls._guard_endpoint(func, "POST"),
                    methods=["POST"],
                    tags=kwargs.get("tags", cls.tags),
                    **kwargs,  # type: ignore
                )

            setattr(_wrapper, __VIEW_ROUTE__, True)
            return _wrapper

        return wrapper

    @classmethod
    def patch(cls, path: str, **kwargs: Unpack[RouterParams]):
        def wrapper(func):
            def _wrapper(cls: "View"):
                return APIRoute(
                    path=cls.prefix + path,
                    endpoint=cls._guard_endpoint(func, "PATCH"),
                    methods=["PATCH"],
                    tags=kwargs.get("tags", cls.tags),
                    **kwargs,  # type: ignore
                )

            setattr(_wrapper, __VIEW_ROUTE__, True)
            return _wrapper

        return wrapper

    @classmethod
    def put(cls, path: str, **kwargs: Unpack[RouterParams]):
        def wrapper(func):
            def _wrapper(cls: "View"):
                return APIRoute(
                    path=cls.prefix + path,
                    endpoint=cls._guard_endpoint(func, "PUT"),
                    methods=["PUT"],
                    tags=kwargs.get("tags", cls.tags),
                    **kwargs,  # type: ignore
                )

            setattr(_wrapper, __VIEW_ROUTE__, True)
            return _wrapper

        return wrapper

    @classmethod
    def delete(cls, path: str, **kwargs: Unpack[RouterParams]):
        def wrapper(func):
            def _wrapper(cls: "View"):
                return APIRoute(
                    path=cls.prefix + path,
                    endpoint=cls._guard_endpoint(func, "DELETE"),
                    methods=["DELETE"],
                    tags=kwargs.get("tags", cls.tags),
                    **kwargs,  # type: ignore
                )

            setattr(_wrapper, __VIEW_ROUTE__, True)
            return _wrapper

        return wrapper
