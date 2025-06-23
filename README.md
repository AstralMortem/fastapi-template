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

## How to use

First you need clone this repo

```
git clone https://github.com/AstralMortem/fastapi-template.git
```

Project use [Poetry](https://python-poetry.org/) as dependency manager. After cloning repo, open it in IDE and install all dependencies.

```
poetry install
```

Now you can extend this template with your needs. To use project CLI use `manage.py`. To run dev server call command:

```
python src/project/manage.py dev
```

To make migration use:

```
python src/project/manage.py makemigrations "init"
```

And for alter DB, use `migrate` command:

```
python src/project/manage.py migrate
```


## View Example

For best DX, I create custom CBV class `View` highly inspired by [fastapi-utils](https://github.com/fastapiutils/fastapi-utils). It have same options as `View` in fastapi-utils, and some extra features:

- Detect if method under route have `Depends(Authorization())` in args and pass resource field to instance, which allow use RBAC and protect every route
- Every class attributes(if not marked as ClassVar type) automaticly resolve dependencies. It support type annotation `service: Annotation[<object>, Depends(<func>)]` or direct assign `service = Depends(<func>)`
- If your view have only CRUD endpoints for one Model, you can use `auto_guard = True` flag, which use mapped 'Method:Action' dict `guard_map` to set corresponding method to permission action.


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
