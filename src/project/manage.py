from project.core.asgi import create_app
from project.core.cli import cli

app = create_app()

if __name__ == "__main__":
    cli()
