# FastAPI Template

Ready to use fastapi template for backend developing

## Features:

 - Async SQLAlchemy ORM out the box.
 - User authentication on JWT tokens.
 - Role-based access controll support.
 - Class-based view with deep Auth(RBAC) integration.
 - Ready to use routes(login, signup, users crud, etc.)
 - Service-Repository pattern with full type hinting under the hood.
 - Simple CLI managment powered by `Typer`

# Code Guideline

 1. Inside package use relative import, such as `from .auth import User`
 2. If object not imported inside `__init__.py`, then use full import: `from project.core.logger import log`, but `from project.model import User`
 3. All Annotated dependencies from `repositories`, `services` packages, must be imported to `__init__.py` file. All dependencies must be imported to `project.dependencies` module.
 4. Annotated dependency must have proper naming: `<Name>Dep = Annotated[<Class>, Depends()]
 5. All object(Class) in `models` and `schemas` package must be imported to `__init__.py` except objects from `base.py` files.
