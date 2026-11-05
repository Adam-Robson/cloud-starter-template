from datetime import datetime

from pydantic import Field

from backend.lib.models.base import ApiModel


class CreateItem(ApiModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class Item(CreateItem):
    id: str
    created_at: datetime
