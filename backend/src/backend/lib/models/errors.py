from typing import Any

from backend.lib.models.base import ApiModel


class ErrorResponse(ApiModel):
    '''Standard error body returned by this API.'''

    status_code: int
    message: str
    detail: Any = None
