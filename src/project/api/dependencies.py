from fastapi_pagination import Params
from typing import Annotated
from fastapi import Depends

PaginationDep = Annotated[Params, Depends()]
