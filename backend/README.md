# BACKEND

Python backend environment managed by uv.

## Clients & Models

- `backend.lib.models`: Pydantic shapes for HTTP payloads. Subclass `ApiModel`
  so fields are snake_case in Python and camelCase in JSON, which suits a
  TypeScript frontend. Includes `ErrorResponse` and a generic `Page[T]`.
- `backend.lib.exceptions`: shared exceptions, plus the handlers that return
  every API error in the `ErrorResponse` shape.
- `backend.clients`: `AsyncHttpClient`, a typed async wrapper over `httpx`.
  Request bodies are `ApiModel` instances, and responses are validated into
  `response_model`. Non-2xx responses raise `HttpStatusError`, and network
  failures raise `HttpTransportError` (both from `backend.lib.exceptions`).
- `backend.db`: storage behind `Protocol`s such as `ItemRepository`.

```python
from backend.clients import AsyncHttpClient
from backend.lib.models import ApiModel, Page


class Widget(ApiModel):
    widget_id: str
    display_name: str


class WidgetClient(AsyncHttpClient):
    async def get_widget(self, widget_id: str) -> Widget:
        return await self.get(f'/widgets/{widget_id}', response_model=Widget)

    async def list_widgets(self, page: int = 1) -> Page[Widget]:
        return await self.get(
            '/widgets', response_model=Page[Widget], params={'page': page}
        )


async with WidgetClient(base_url='https://api.example.com') as client:
    widget = await client.get_widget('w1')
```

In tests, pass `transport=httpx.MockTransport(handler)` to stub responses (see
`test/test_clients.py`).

## Checks

Run from `backend/`:

```sh
uv run ruff check .          # lint
uv run ruff format --check . # formatting
uv run mypy                  # strict type checking
uv run pytest                # tests + coverage
```
