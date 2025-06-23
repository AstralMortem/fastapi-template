from fastapi import FastAPI
from project.config import settings
from .exceptions import set_app_exception
from .middlewares import LoggingMiddleware

MIDDLEWARES = [LoggingMiddleware]


def set_router(app: FastAPI):
    from project.api import api_router

    app.include_router(api_router)


def set_middlewares(app: FastAPI):
    for middleware in MIDDLEWARES:
        app.add_middleware(middleware)


def create_app():
    app = FastAPI(debug=settings.DEBUG)

    set_middlewares(app)
    set_app_exception(app)
    set_router(app)

    return app
