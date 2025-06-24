from fastapi_filter.contrib.sqlalchemy import Filter
from project.models import Role, Permission

class RoleFilter(Filter):
    class Constants(Filter.Constants):
        model = Role


class PermissionFilter(Filter):
    class Constants(Filter.Constants):
        model = Permission