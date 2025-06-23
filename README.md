# FastAPI Template

Ready to use fastapi template for backend developing

## Features:

 - Async `SQLAlchemy` ORM out the box.
 - User authentication on `JWT` tokens.
 - `Role-Based Access Controll` support.
 - `Class-Based View` with deep Auth(RBAC) integration.
 - Ready to use routes(login, signup, users crud, etc.)
 - `Service-Repository pattern` with full type hinting under the hood.
 - Simple `CLI` managment powered by `Typer`


## View Example 

``` python
from project.core.cbv import View
from project.core.security import HasPermission, Action
from project.schemas import AccessToken
from fastapi import Depends, FastAPI

class TestView(View):
    prefix = "/tests"
    tags = ["Test"]
    resource = "test" # For permission table

    # Annotation to service dependency, like:  
    # TestServiceDep = Annotated[TestService, Depends(get_test_service)]
    service: TestServiceDep 

    @View.get("/")
    async def get_test(self):
        return {"Hello": "World"}

    # Protected route. If user have test:read permission, can retrieve token
    @View.get("/protected", response_model = AccessToken)
    async def get_protected(self, token: AccessToken = Depends(HasPermission(Action.READ))):
        return token

app = FastAPI()

app.include_router(TestView.as_router())

```



# Code Guideline

 1. Inside package use relative import, such as `from .auth import User`
 2. If object not imported inside `__init__.py`, then use full import: `from project.core.logger import log`, but `from project.model import User`
 3. All Annotated dependencies from `repositories`, `services` packages, must be imported to `__init__.py` file. All dependencies must be imported to `project.dependencies` module.
 4. Annotated dependency must have proper naming: `<Name>Dep = Annotated[<Class>, Depends()]
 5. All object(Class) in `models` and `schemas` package must be imported to `__init__.py` except objects from `base.py` files.
