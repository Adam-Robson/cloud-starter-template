from typing import Literal

from backend.lib.models.base import ApiModel


class HealthResponse(ApiModel):
    status: Literal['ok']
    version: str
