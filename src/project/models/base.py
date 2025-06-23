from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr
from sqlalchemy import DateTime, func
from datetime import datetime
from project.utils.string import make_plural, camel2snake


class TimestampMixin:
    """
    Mixin class to add created_at and updated_at timestamps to a model.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), server_onupdate=func.now()
    )


class Model(DeclarativeBase):
    """
    Base class for all sqlalchemy models.
    """

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return make_plural(camel2snake(cls.__name__))
