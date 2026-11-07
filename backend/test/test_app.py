from importlib.metadata import version

import httpx
from pytest_mock import MockerFixture

from backend.config import DEFAULT_CORS_ORIGINS, Settings
from backend.main import app, main, settings


async def test_health(api_client: httpx.AsyncClient) -> None:
    response = await api_client.get('/api/health')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok', 'version': version('backend')}


async def test_unknown_route_returns_error_response(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.get('/api/nope')
    assert response.status_code == 404
    assert response.json()['message'] == 'Not Found'


async def test_cors_allows_configured_origin(
    api_client: httpx.AsyncClient, frontend_origin: str
) -> None:
    response = await api_client.options(
        '/api/items',
        headers={
            'Origin': frontend_origin,
            'Access-Control-Request-Method': 'POST',
        },
    )
    assert response.headers['access-control-allow-origin'] == frontend_origin


async def test_cors_rejects_other_origin(
    api_client: httpx.AsyncClient,
) -> None:
    response = await api_client.get(
        '/api/health', headers={'Origin': 'http://evil.test'}
    )
    assert 'access-control-allow-origin' not in response.headers


def test_settings_from_env() -> None:
    settings = Settings.from_env(
        {'CORS_ORIGINS': 'http://a.test, http://b.test,', 'PORT': '9000'}
    )
    assert settings == Settings(
        cors_origins=('http://a.test', 'http://b.test'), port=9000
    )


def test_settings_defaults() -> None:
    settings = Settings.from_env({})
    assert settings.cors_origins == tuple(DEFAULT_CORS_ORIGINS.split(','))
    assert settings.port == 8080


def test_main_runs_uvicorn(mocker: MockerFixture) -> None:
    run = mocker.patch('backend.main.uvicorn.run')
    main()
    run.assert_called_once_with(app, host='0.0.0.0', port=settings.port)
