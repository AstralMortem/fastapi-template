from project.core.cbv import View
from project.schemas import UserCreate, UserRead, TokenResponse
from project.dependencies import AuthServiceDep
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends


class AuthView(View):
    prefix = "/auth"
    tags = ["Auth"]
    resource = "auth"

    service: AuthServiceDep

    @View.post("/login", response_model=TokenResponse)
    async def login(self, credentials: OAuth2PasswordRequestForm = Depends()):
        return await self.service.login(credentials.username, credentials.password)

    @View.post("/signup", response_model=UserRead)
    async def signup(self, payload: UserCreate):
        return await self.service.signup(payload, True)
