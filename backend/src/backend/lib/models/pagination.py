from pydantic import Field

from backend.lib.models.base import ApiModel


class Page[T](ApiModel):
    '''Envelope for paginated list responses.'''

    items: list[T]
    total: int = Field(ge=0)
    page: int = Field(default=1, ge=1)
    page_size: int = Field(ge=1)

    @property
    def has_next(self) -> bool:
        return self.page * self.page_size < self.total
