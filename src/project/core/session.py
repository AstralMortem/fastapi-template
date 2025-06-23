from typing import Annotated

from fastapi import Depends
from sqlalchemy import Delete, Insert, Update
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session
from project.config import settings
from .logger import log

engines = {
    "writer": create_async_engine(str(settings.DATABASE_URL), pool_recycle=3600),
    "reader": create_async_engine(str(settings.DATABASE_URL), pool_recycle=3600),
}


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kwargs):
        if self._flushing or isinstance(clause, (Update, Delete, Insert)):
            return engines["writer"].sync_engine
        return engines["reader"].sync_engine


session_factory = async_sessionmaker(
    class_=AsyncSession, sync_session_class=RoutingSession, expire_on_commit=False
)


async def get_session():
    async with session_factory() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            log.error(e)
            raise e
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
