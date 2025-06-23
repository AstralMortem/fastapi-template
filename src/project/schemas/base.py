from pydantic import BaseModel, ConfigDict
from datetime import datetime


class TimestampModelMixin:
    created_at: datetime
    updated_at: datetime


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ReadSchema(Schema):
    pass


class CreateSchema(Schema):
    pass


class UpdateSchema(Schema):
    pass
