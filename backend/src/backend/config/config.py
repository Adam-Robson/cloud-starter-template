from collections.abc import Mapping
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, field_validator, model_validator

DEFAULT_CORS_ORIGINS = 'http://localhost:5173,http://localhost:3000'
DEFAULT_PORT = '8080'

type Storage = Literal['memory', 'firestore']

DEFAULT_STORAGE: Storage = 'memory'


class Settings(BaseModel):
    '''Runtime configuration, read from the environment (12-factor).'''

    model_config = ConfigDict(frozen=True)

    cors_origins: tuple[str, ...]
    port: int
    storage: Storage = DEFAULT_STORAGE
    gcp_project_id: str | None = None

    @model_validator(mode='after')
    def _require_project_for_firestore(self) -> Self:
        if self.storage == 'firestore' and not self.gcp_project_id:
            raise ValueError('GCP_PROJECT_ID is required for firestore')
        return self

    @field_validator('cors_origins', mode='before')
    @classmethod
    def _split_origins(cls, value: object) -> object:
        '''Accept a comma-separated string, as set in the environment.'''
        if not isinstance(value, str):
            return value
        origins = (origin.strip() for origin in value.split(','))
        return tuple(origin for origin in origins if origin)

    @classmethod
    def from_env(cls, environ: Mapping[str, str]) -> Self:
        return cls.model_validate(
            {
                'cors_origins': environ.get(
                    'CORS_ORIGINS', DEFAULT_CORS_ORIGINS
                ),
                'port': environ.get('PORT', DEFAULT_PORT),
                'storage': environ.get('STORAGE', DEFAULT_STORAGE),
                'gcp_project_id': environ.get('GCP_PROJECT_ID') or None,
            }
        )
