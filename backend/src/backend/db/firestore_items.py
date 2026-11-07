from datetime import UTC, datetime

from google.api_core.exceptions import NotFound
from google.cloud.firestore import (
    AsyncClient,
    AsyncCollectionReference,
    AsyncDocumentReference,
)
from google.cloud.firestore_v1.async_aggregation import AsyncAggregationQuery
from google.cloud.firestore_v1.base_document import DocumentSnapshot

from backend.lib.models.items import CreateItem, Item

ORDER_FIELD = 'created_at'
COUNT_ALIAS = 'total'


class FirestoreItemRepository:
    '''Items stored as documents in one Firestore collection.

    Fields are stored snake_case; the document id is the item id.
    '''

    def __init__(self, collection: AsyncCollectionReference) -> None:
        self._collection = collection

    async def list_page(
        self, offset: int, limit: int
    ) -> tuple[list[Item], int]:
        query = (
            self._collection.order_by(ORDER_FIELD).offset(offset).limit(limit)
        )
        items = [_to_item(snapshot) async for snapshot in query.stream()]
        return items, await self._count()

    async def get(self, item_id: str) -> Item | None:
        snapshot = await self._collection.document(item_id).get()
        return _to_item(snapshot) if snapshot.exists else None

    async def add(self, data: CreateItem) -> Item:
        reference = self._collection.document()
        item = Item(
            id=reference.id,
            created_at=datetime.now(UTC),
            **data.model_dump(by_alias=False),
        )
        await reference.set(item.model_dump(by_alias=False, exclude={'id'}))
        return item

    async def remove(self, item_id: str) -> bool:
        '''Delete only if present, so a missing id reports False.'''
        try:
            await self._collection.document(item_id).delete(
                option=AsyncClient.write_option(exists=True)
            )
        except NotFound:
            return False
        return True

    async def _count(self) -> int:
        '''Server-side count aggregation; no documents are read.'''
        aggregation = AsyncAggregationQuery(self._collection)
        aggregation.count(alias=COUNT_ALIAS)
        results = await aggregation.get()
        return int(results[0][0].value)


def _to_item(snapshot: DocumentSnapshot[AsyncDocumentReference]) -> Item:
    data = snapshot.to_dict() or {}
    return Item.model_validate({**data, 'id': snapshot.id})
