from datetime import UTC, datetime
from typing import Protocol
from uuid import uuid4

from backend.lib.models.items import CreateItem, Item


class ItemRepository(Protocol):
    '''Storage for items; swap the implementation without touching routes.'''

    async def list_page(
        self, offset: int, limit: int
    ) -> tuple[list[Item], int]: ...

    async def get(self, item_id: str) -> Item | None: ...

    async def add(self, data: CreateItem) -> Item: ...

    async def remove(self, item_id: str) -> bool: ...


class InMemoryItemRepository:
    '''Process-local store for development and tests; not persistent.'''

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}

    async def list_page(
        self, offset: int, limit: int
    ) -> tuple[list[Item], int]:
        items = list(self._items.values())
        return items[offset : offset + limit], len(items)

    async def get(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    async def add(self, data: CreateItem) -> Item:
        item = Item(
            id=str(uuid4()),
            created_at=datetime.now(UTC),
            **data.model_dump(by_alias=False),
        )
        self._items[item.id] = item
        return item

    async def remove(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None
