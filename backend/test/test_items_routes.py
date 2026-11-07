import httpx

from backend.db import InMemoryItemRepository
from backend.lib.models import CreateItem


async def test_create_returns_camel_case_item(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.post(
        '/api/items', json={'name': 'Gear', 'description': 'Small'}
    )
    assert response.status_code == 201
    body = response.json()
    assert body['name'] == 'Gear'
    assert body['description'] == 'Small'
    assert set(body) == {'id', 'name', 'description', 'createdAt'}


async def test_create_rejects_invalid_body(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.post('/api/items', json={'name': ''})
    assert response.status_code == 422
    body = response.json()
    assert body['statusCode'] == 422
    assert body['message'] == 'Request validation failed'
    assert body['detail'][0]['loc'] == ['body', 'name']


async def test_get_returns_item(
    api_client: httpx.AsyncClient,
    item_repository: InMemoryItemRepository,
) -> None:
    item = await item_repository.add(CreateItem(name='Gear'))
    response = await api_client.get(f'/api/items/{item.id}')
    assert response.status_code == 200
    assert response.json()['id'] == item.id


async def test_get_missing_item_returns_error_response(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.get('/api/items/missing')
    assert response.status_code == 404
    assert response.json() == {
        'statusCode': 404,
        'message': 'Item not found',
        'detail': None,
    }


async def test_list_paginates(
    api_client: httpx.AsyncClient,
    item_repository: InMemoryItemRepository,
) -> None:
    for name in ('a', 'b', 'c'):
        await item_repository.add(CreateItem(name=name))
    response = await api_client.get(
        '/api/items', params={'page': 2, 'pageSize': 2}
    )
    body = response.json()
    assert [item['name'] for item in body['items']] == ['c']
    assert body['total'] == 3
    assert body['page'] == 2
    assert body['pageSize'] == 2


async def test_delete_removes_item(
    api_client: httpx.AsyncClient,
    item_repository: InMemoryItemRepository,
) -> None:
    item = await item_repository.add(CreateItem(name='Gear'))
    response = await api_client.delete(f'/api/items/{item.id}')
    assert response.status_code == 204
    assert await item_repository.get(item.id) is None


async def test_delete_missing_item_returns_404(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.delete('/api/items/missing')
    assert response.status_code == 404
