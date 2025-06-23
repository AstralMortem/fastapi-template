from typer import Typer
from project.config import settings
from alembic import command
from alembic.config import Config

migrations_cli = Typer()
alembic_cfg = Config(settings.ALEMBIC_INI_PATH)


@migrations_cli.command()
def makemigrations(m: str | None = None, autogenerate: bool = True, sql: bool = False):
    if m is None:
        m = "init"
    command.revision(alembic_cfg, message=m, autogenerate=autogenerate, sql=sql)


@migrations_cli.command()
def migrate(revision: str = "heads", sql: bool = False):
    command.upgrade(alembic_cfg, revision, sql=sql)


@migrations_cli.command()
def downgrade(revision: str, sql: bool = False):
    command.downgrade(alembic_cfg, revision, sql=sql)


__all__ = ["migrations_cli"]
