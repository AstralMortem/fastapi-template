from fastapi import APIRouter
from project.config import settings
from .v1 import v1_router

api_router = APIRouter(prefix=settings.GLOBAL_API_PREFIX)

api_router.include_router(v1_router)
