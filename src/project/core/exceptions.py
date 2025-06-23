from project.config import settings
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request
from starlette import status as http_status


class BackendException(Exception):
    def __init__(
        self,
        code: int,
        title: str,
        message: str | None,
        debug: Exception | None = None,
        headers: dict | None = None,
    ):
        self.code = code
        self.title = title
        self.message = message
        self.debug = str(debug) if debug else None
        self.headers = headers if headers else {}

    def to_response(self):
        payload = {
            "status_code": self.code,
            "title": self.title,
            "message": self.message,
            "debug": self.debug if settings.DEBUG else None,
        }

        error = JSONResponse(status_code=self.code, content=payload)
        return error


def set_app_exception(app: FastAPI):
    @app.exception_handler(BackendException)
    async def backend_exception_handler(request: Request, exc: BackendException):
        return exc.to_response()


__all__ = ["BackendException", "http_status", "set_app_exception"]
