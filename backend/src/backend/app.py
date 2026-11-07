from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import Settings
from backend.db import ItemRepository, create_item_repository
from backend.lib.exceptions.handlers import EXCEPTION_HANDLERS
from backend.routes import api_router


def create_app(
    settings: Settings, item_repository: ItemRepository | None = None
) -> FastAPI:
    '''Build the API; dependencies are injected so tests can swap them.'''
    app = FastAPI(title='backend', exception_handlers=EXCEPTION_HANDLERS)
    app.state.item_repository = item_repository or create_item_repository(
        settings
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.include_router(api_router)
    return app
