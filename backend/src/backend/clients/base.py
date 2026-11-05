'''Async wrapper around httpx for calling HTTP services.'''

from collections.abc import Mapping
from types import TracebackType
from typing import Any, Self, Unpack

import httpx
from pydantic import TypeAdapter

from backend.clients.request_options import RequestOptions
from backend.lib.exceptions import HttpStatusError, HttpTransportError


class AsyncHttpClient:
    '''Typed async wrapper around httpx for calling HTTP services.

    ``send`` performs the call and maps failures to client errors;
    ``request`` and the verb helpers also validate the response body into
    ``response_model``, which may be a model, ``list[Model]`` or
    ``Page[Model]``.

    Subclass it per upstream service and expose typed methods::

        class WidgetClient(AsyncHttpClient):
            async def get_widget(self, widget_id: str) -> Widget:
                return await self.get(f'/widgets/{widget_id}', Widget)

        async with WidgetClient(base_url='https://api.example.com') as c:
            widget = await c.get_widget('abc')
    '''

    def __init__(
        self,
        base_url: str,
        *,
        headers: Mapping[str, str] | None = None,
        timeout: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            timeout=timeout,
            transport=transport,
        )

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def send(
        self, method: str, path: str, **options: Unpack[RequestOptions]
    ) -> httpx.Response:
        model = options.get('json')
        body = (
            model.model_dump(mode='json', by_alias=True, exclude_none=True)
            if model is not None
            else None
        )
        try:
            response = await self._client.request(
                method,
                path,
                json=body,
                params=options.get('params'),
                headers=options.get('headers'),
            )
        except httpx.TransportError as e:
            raise HttpTransportError(method, path, e) from e

        if not response.is_success:
            raise HttpStatusError(
                method,
                str(response.url),
                response.status_code,
                _read_body(response),
            )
        return response

    async def request[T](
        self,
        method: str,
        path: str,
        response_model: type[T],
        **options: Unpack[RequestOptions],
    ) -> T:
        response = await self.send(method, path, **options)
        return TypeAdapter(response_model).validate_json(response.content)

    async def get[T](
        self,
        path: str,
        response_model: type[T],
        **options: Unpack[RequestOptions],
    ) -> T:
        return await self.request('GET', path, response_model, **options)

    async def post[T](
        self,
        path: str,
        response_model: type[T],
        **options: Unpack[RequestOptions],
    ) -> T:
        return await self.request('POST', path, response_model, **options)

    async def put[T](
        self,
        path: str,
        response_model: type[T],
        **options: Unpack[RequestOptions],
    ) -> T:
        return await self.request('PUT', path, response_model, **options)

    async def patch[T](
        self,
        path: str,
        response_model: type[T],
        **options: Unpack[RequestOptions],
    ) -> T:
        return await self.request('PATCH', path, response_model, **options)

    async def delete(
        self, path: str, **options: Unpack[RequestOptions]
    ) -> None:
        await self.send('DELETE', path, **options)


def _read_body(response: httpx.Response) -> Any:
    '''Parse an error body as JSON, falling back to raw text.'''
    try:
        return response.json()
    except ValueError:
        return response.text
