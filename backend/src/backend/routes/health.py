from importlib.metadata import version

from fastapi import APIRouter

from backend.lib.models.health import HealthResponse

router = APIRouter(tags=['health'])


@router.get('/health')
async def health() -> HealthResponse:
    return HealthResponse(status='ok', version=version('backend'))
