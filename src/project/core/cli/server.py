from tkinter import N
from typer import Typer
from project.config import settings
from pathlib import Path
import uvicorn

server_cli = Typer(rich_markup_mode="rich")
MANAGE_PY_PATH = settings.PROJECT_DIR.joinpath("manage.py")


def get_asgi_string(path: str | Path):
    return (
        Path(path)
        .relative_to(Path.cwd())
        .as_posix()
        .replace("/", ".")
        .replace(".py", ":app")
        .replace("src.", "")
    )


def _run(path: str | None, host: str, port: int, reload: bool):
    asgi = get_asgi_string(path or MANAGE_PY_PATH)
    uvicorn.run(asgi, host=host, port=port, reload=reload, access_log=False)


@server_cli.command()
def dev(
    path: str | None = None, host: str = "127.0.0.1", port: int = 8000, reload: bool = True
):
    _run(path, host, port, reload)


@server_cli.command()
def prod(
    path: str | None = None, host: str = "0.0.0.0", port: int = 8000, reload: bool = False
):
    _run(path, host, port, reload)
