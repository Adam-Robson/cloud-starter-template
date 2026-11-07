import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from backend.config import Settings
from backend.db import (
    FirestoreItemRepository,
    InMemoryItemRepository,
    create_item_repository,
)


@pytest.fixture
def firestore_settings() -> Settings:
    return Settings.from_env(
        {'STORAGE': 'firestore', 'GCP_PROJECT_ID': 'sandbox'}
    )


def test_storage_defaults_to_memory() -> None:
    settings = Settings.from_env({})
    assert settings.storage == 'memory'
    assert settings.gcp_project_id is None


def test_storage_reads_firestore_settings(
    firestore_settings: Settings,
) -> None:
    assert firestore_settings.storage == 'firestore'
    assert firestore_settings.gcp_project_id == 'sandbox'


def test_firestore_requires_project_id() -> None:
    with pytest.raises(ValidationError, match='GCP_PROJECT_ID'):
        Settings.from_env({'STORAGE': 'firestore', 'GCP_PROJECT_ID': ''})


def test_unknown_storage_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings.from_env({'STORAGE': 'postgres'})


def test_memory_storage_builds_in_memory_repository() -> None:
    repository = create_item_repository(Settings.from_env({}))
    assert isinstance(repository, InMemoryItemRepository)


def test_firestore_storage_builds_firestore_repository(
    firestore_settings: Settings, mocker: MockerFixture
) -> None:
    client = mocker.patch('backend.db.factory.AsyncClient')

    repository = create_item_repository(firestore_settings)

    assert isinstance(repository, FirestoreItemRepository)
    client.assert_called_once_with(project='sandbox')
    client.return_value.collection.assert_called_once_with('items')
