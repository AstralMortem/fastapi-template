from .base import Schema
from project.utils.jwts import JWTPayload


class AccessToken(JWTPayload):
    email: str
    permissions: list[str] = []
    role: str = []


class TokenResponse(Schema):
    access_token: str
    token_type: str = "Bearer"
