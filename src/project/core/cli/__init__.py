from typer import Typer
from .migrations import migrations_cli
from .server import server_cli

cli = Typer(rich_markup_mode="rich")
cli.add_typer(migrations_cli)
cli.add_typer(server_cli)
__all__ = ["cli"]
