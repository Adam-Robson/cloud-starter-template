from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from backend.db.items import ItemRepository
from backend.lib.models.items import CreateItem, Item
from backend.lib.models.pagination import Page

router = APIRouter(prefix='/items', tags=['items'])


def get_item_repository(request: Request) -> ItemRepository:
    repository: ItemRepository = request.app.state.item_repository
    return repository


Repository = Annotated[ItemRepository, Depends(get_item_repository)]


@router.get('')
async def list_items(
    repository: Repository,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias='pageSize', ge=1, le=100)] = 20,
) -> Page[Item]:
    items, total = await repository.list_page(
        offset=(page - 1) * page_size, limit=page_size
    )
    return Page[Item](items=items, total=total, page=page, page_size=page_size)


@router.get('/{item_id}')
async def get_item(item_id: str, repository: Repository) -> Item:
    item = await repository.get(item_id)
    if item is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Item not found')
    return item


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_item(data: CreateItem, repository: Repository) -> Item:
    return await repository.add(data)


@router.delete('/{item_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: str, repository: Repository) -> None:
    if not await repository.remove(item_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, 'Item not found')
