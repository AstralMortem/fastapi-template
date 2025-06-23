from .base import Model, TimestampMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from project.config import settings
import uuid


class RolePermissionRel(Model):
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"), primary_key=True)


class Permission(TimestampMixin, Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    resource: Mapped[str]
    action: Mapped[str]


class Role(Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    permissions: Mapped[list[Permission]] = relationship(
        lazy="selectin", secondary=RolePermissionRel.__table__
    )


class User(TimestampMixin, Model):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=settings.DEFAULT_USER_IS_ACTIVE)
    is_verified: Mapped[bool] = mapped_column(default=settings.DEFAULT_USER_IS_VERIFIED)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    role: Mapped[Role] = relationship(lazy="joined")
