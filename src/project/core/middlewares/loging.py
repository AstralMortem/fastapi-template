# middlewares/logging_middleware.py

import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from colorama import Fore, Style
from project.core.logger import log


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = (time.time() - start_time) * 1000  # ms

        method = self._color_method(request.method)
        status = self._color_status(response.status_code)
        url = f"{request.url.path}" + f"?{request.url.query}" if request.url.query else None
        if request.client:
            client_ip = request.client.host

        log.info(
            f"{method} {url} - {status} - {duration:.1f}ms - {Fore.BLUE}{client_ip}{Style.RESET_ALL}"
        )
        return response

    def _color_method(self, method: str) -> str:
        return {
            "GET": f"{Fore.CYAN}GET{Style.RESET_ALL}",
            "POST": f"{Fore.GREEN}POST{Style.RESET_ALL}",
            "PUT": f"{Fore.MAGENTA}PUT{Style.RESET_ALL}",
            "PATCH": f"{Fore.YELLOW}PATCH{Style.RESET_ALL}",
            "DELETE": f"{Fore.RED}DELETE{Style.RESET_ALL}",
        }.get(method.upper(), method)

    def _color_status(self, status_code: int) -> str:
        if 200 <= status_code < 300:
            return f"{Fore.GREEN}{status_code}{Style.RESET_ALL}"
        elif 300 <= status_code < 400:
            return f"{Fore.CYAN}{status_code}{Style.RESET_ALL}"
        elif 400 <= status_code < 500:
            return f"{Fore.YELLOW}{status_code}{Style.RESET_ALL}"
        else:
            return f"{Fore.RED}{status_code}{Style.RESET_ALL}"
