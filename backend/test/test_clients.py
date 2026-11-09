import json
from collections.abc import AsyncIterator

import httpx
import pytest

from backend.clients import AsyncHttpClient
from backend.lib.exceptions import HttpStatusError, HttpTransportError
from backend.lib.models import ApiModel, Page

WIDGET = {'widgetId': 'w1', 'displayName': 'Gear'}


class Widget(ApiModel):
    widget_id: str
    display_name: str


class CreateWidget(ApiModel):
    display_name: str
    description: str | None = None


def _handler(request: httpx.Request) -> httpx.Response:
    match (request.method, request.url.path):
        case ('GET', '/widgets/w1'):
            return httpx.Response(200, json=WIDGET)
        case ('GET', '/widgets'):
            return httpx.Response(200, json=[WIDGET])
        case ('GET', '/widgets/paged'):
            page = int(request.url.params['page'])
            return httpx.Response(
                200,
                json={
                    'items': [WIDGET],
                    'total': 1,
                    'page': page,
                    'pageSize': 10,
                },
            )
        case ('POST', '/widgets'):
            # Echo the body back so tests can inspect what was sent.
            return httpx.Response(201, json=json.loads(request.content))
        case ('DELETE', '/widgets/w1'):
            return httpx.Response(204)
        case ('GET', '/down'):
            raise httpx.ConnectError('connection refused', request=request)
        case ('GET', '/text-error'):
            return httpx.Response(502, text='Bad Gateway')
        case _:
            return httpx.Response(404, json={'message': 'Not found'})


@pytest.fixture
def http_transport() -> httpx.MockTransport:
    return httpx.MockTransport(_handler)


@pytest.fixture
async def client(
    http_transport: httpx.MockTransport,
) -> AsyncIterator[AsyncHttpClient]:
    async with AsyncHttpClient(
        'http://testserver', transport=http_transport
    ) as client:
        yield client


async def test_get_parses_model(client: AsyncHttpClient) -> None:
    widget = await client.get('/widgets/w1', response_model=Widget)
    assert widget == Widget(widget_id='w1', display_name='Gear')


async def test_get_parses_list(client: AsyncHttpClient) -> None:
    widgets = await client.get('/widgets', response_model=list[Widget])
    assert [w.widget_id for w in widgets] == ['w1']


async def test_get_parses_page_with_params(client: AsyncHttpClient) -> None:
    page = await client.get(
        '/widgets/paged', response_model=Page[Widget], params={'page': 2}
    )
    assert page.page == 2
    assert page.items[0].display_name == 'Gear'


async def test_post_sends_camel_case_without_nones(
    client: AsyncHttpClient,
) -> None:
    echoed = await client.post(
        '/widgets',
        json=CreateWidget(display_name='Gear'),
        response_model=dict[str, str],
    )
    assert echoed == {'displayName': 'Gear'}


async def test_send_returns_raw_response(client: AsyncHttpClient) -> None:
    response = await client.send('DELETE', '/widgets/w1')
    assert response.status_code == 204


async def test_delete_accepts_empty_body(client: AsyncHttpClient) -> None:
    # Typed as returning None, so success is simply not raising on a 204.
    await client.delete('/widgets/w1')


async def test_error_status_raises_with_json_body(
    client: AsyncHttpClient,
) -> None:
    with pytest.raises(HttpStatusError) as exc_info:
        await client.get('/missing', response_model=Widget)
    assert exc_info.value.status_code == 404
    assert exc_info.value.body == {'message': 'Not found'}


async def test_error_status_raises_with_text_body(
    client: AsyncHttpClient,
) -> None:
    with pytest.raises(HttpStatusError) as exc_info:
        await client.send('GET', '/text-error')
    assert exc_info.value.status_code == 502
    assert exc_info.value.body == 'Bad Gateway'


async def test_transport_failure_raises(client: AsyncHttpClient) -> None:
    with pytest.raises(HttpTransportError) as exc_info:
        await client.send('GET', '/down')
    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)


async def test_put_and_patch_route_methods(
    http_transport: httpx.MockTransport,
) -> None:
    seen: list[str] = []

    def record(request: httpx.Request) -> httpx.Response:
        seen.append(request.method)
        return httpx.Response(200, json=WIDGET)

    async with AsyncHttpClient(
        'http://testserver', transport=httpx.MockTransport(record)
    ) as client:
        await client.put('/widgets/w1', response_model=Widget)
        await client.patch('/widgets/w1', response_model=Widget)
    assert seen == ['PUT', 'PATCH']
