from .auth import User, Role, Permission

# for alembic automigration purposes
from .base import Model

__all__ = ["User", "Role", "Permission", "Model"]
