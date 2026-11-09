# Configuration for pytest fixtures and plugins
from collections.abc import AsyncIterator, Iterator

import httpx
import pytest

from backend.app import create_app
from backend.config import Settings
from backend.db import InMemoryItemRepository


def _default_handler(request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={})


@pytest.fixture
def http_transport() -> httpx.MockTransport:
    '''Override in a test module to stub specific responses.'''
    return httpx.MockTransport(_default_handler)


@pytest.fixture
def http_client(
    http_transport: httpx.MockTransport,
) -> Iterator[httpx.Client]:
    with httpx.Client(
        transport=http_transport, base_url='http://testserver'
    ) as client:
        yield client


@pytest.fixture
async def async_http_client(
    http_transport: httpx.MockTransport,
) -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=http_transport, base_url='http://testserver'
    ) as client:
        yield client


@pytest.fixture
def item_repository() -> InMemoryItemRepository:
    return InMemoryItemRepository()


@pytest.fixture
def frontend_origin() -> str:
    return 'http://frontend.test'


@pytest.fixture
async def api_client(
    item_repository: InMemoryItemRepository, frontend_origin: str
) -> AsyncIterator[httpx.AsyncClient]:
    '''Calls the API in-process; no server or network needed.'''
    app = create_app(
        Settings(cors_origins=(frontend_origin,), port=8080),
        item_repository=item_repository,
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url='http://testserver'
    ) as client:
        yield client
