from google.cloud.firestore import AsyncClient

from backend.config import Settings
from backend.db.firestore_items import FirestoreItemRepository
from backend.db.items import InMemoryItemRepository, ItemRepository

ITEMS_COLLECTION = 'items'


def create_item_repository(settings: Settings) -> ItemRepository:
    '''Pick the item store named by `settings.storage`.

    Firestore authenticates with Application Default Credentials: the
    service account on Cloud Run, or `gcloud auth application-default
    login` locally. No key files.
    '''
    if settings.storage == 'firestore':
        client = AsyncClient(project=settings.gcp_project_id)
        return FirestoreItemRepository(client.collection(ITEMS_COLLECTION))
    return InMemoryItemRepository()
