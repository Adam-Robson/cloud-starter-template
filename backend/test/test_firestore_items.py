from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from google.api_core.exceptions import NotFound
from google.cloud.firestore import AsyncDocumentReference
from google.cloud.firestore_v1.base_aggregation import AggregationResult
from google.cloud.firestore_v1.base_document import DocumentSnapshot
from pytest_mock import MockerFixture

from backend.db import FirestoreItemRepository
from backend.lib.models import CreateItem, Item

CREATED_AT = datetime(2026, 1, 2, tzinfo=UTC)

type Snapshot = DocumentSnapshot[AsyncDocumentReference]


def snapshot(item_id: str, data: dict[str, Any] | None) -> Snapshot:
    reference = MagicMock(spec=AsyncDocumentReference)
    reference.id = item_id
    return DocumentSnapshot(reference, data, data is not None, None, None, None)


def stored(name: str) -> dict[str, Any]:
    return {'name': name, 'description': None, 'created_at': CREATED_AT}


async def stream(*snapshots: Snapshot) -> AsyncIterator[Snapshot]:
    for each in snapshots:
        yield each


@pytest.fixture
def collection() -> MagicMock:
    '''Stand-in for an AsyncCollectionReference.'''
    return MagicMock()


@pytest.fixture
def repository(collection: MagicMock) -> FirestoreItemRepository:
    return FirestoreItemRepository(collection)


async def test_list_page_queries_in_order_and_counts(
    collection: MagicMock,
    repository: FirestoreItemRepository,
    mocker: MockerFixture,
) -> None:
    query = collection.order_by.return_value.offset.return_value
    query.limit.return_value.stream.return_value = stream(
        snapshot('a', stored('A')), snapshot('b', stored('B'))
    )
    aggregation = mocker.patch(
        'backend.db.firestore_items.AsyncAggregationQuery'
    ).return_value
    aggregation.get = AsyncMock(
        return_value=[[AggregationResult(alias='total', value=7)]]
    )

    items, total = await repository.list_page(offset=2, limit=2)

    assert [item.id for item in items] == ['a', 'b']
    assert items[0] == Item(
        id='a', name='A', description=None, created_at=CREATED_AT
    )
    assert total == 7
    collection.order_by.assert_called_once_with('created_at')
    collection.order_by.return_value.offset.assert_called_once_with(2)
    query.limit.assert_called_once_with(2)
    aggregation.count.assert_called_once_with(alias='total')


async def test_get_returns_item(
    collection: MagicMock, repository: FirestoreItemRepository
) -> None:
    document = collection.document.return_value
    document.get = AsyncMock(return_value=snapshot('a', stored('A')))

    item = await repository.get('a')

    assert item is not None
    assert item.name == 'A'
    collection.document.assert_called_once_with('a')


async def test_get_missing_returns_none(
    collection: MagicMock, repository: FirestoreItemRepository
) -> None:
    document = collection.document.return_value
    document.get = AsyncMock(return_value=snapshot('a', None))

    assert await repository.get('a') is None


async def test_add_stores_snake_case_fields(
    collection: MagicMock, repository: FirestoreItemRepository
) -> None:
    reference = collection.document.return_value
    reference.id = 'new-id'
    reference.set = AsyncMock()

    item = await repository.add(CreateItem(name='Gear', description='Small'))

    assert item.id == 'new-id'
    assert item.name == 'Gear'
    reference.set.assert_awaited_once_with(
        {
            'name': 'Gear',
            'description': 'Small',
            'created_at': item.created_at,
        }
    )


async def test_remove_deletes_existing_document(
    collection: MagicMock, repository: FirestoreItemRepository
) -> None:
    document = collection.document.return_value
    document.delete = AsyncMock()

    assert await repository.remove('a') is True
    option = document.delete.call_args.kwargs['option']
    assert option._exists is True


async def test_remove_missing_returns_false(
    collection: MagicMock, repository: FirestoreItemRepository
) -> None:
    document = collection.document.return_value
    document.delete = AsyncMock(side_effect=NotFound('missing'))

    assert await repository.remove('a') is False
