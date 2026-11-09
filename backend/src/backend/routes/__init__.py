from fastapi import APIRouter

from backend.lib.models.errors import ErrorResponse
from backend.routes.health import router as health_router
from backend.routes.items import router as items_router

# Documents the ErrorResponse shape (see lib.exceptions.handlers) in OpenAPI so
# generated frontend types match what clients actually receive.
api_router = APIRouter(
    prefix='/api',
    responses={'default': {'model': ErrorResponse, 'description': 'Error'}},
)
api_router.include_router(health_router)
api_router.include_router(items_router)

__all__ = ['api_router']
