import datetime
import uuid
from typing import List

from app.models import Tag
from app.repositories import TagRepository
from app.core.exceptions import HTTPBadRequest


class TagService:

    def __init__(self, repository: TagRepository) -> None:
        self._repository: TagRepository = repository

    async def create(self, name: str, user_id: str) -> Tag:
        id = str(uuid.uuid4())
        tag_obj = Tag(name=name, user_id=user_id, id=id)

        await self._repository.create(tag_obj)

        return tag_obj

    async def delete(self, tag_id: str, user_id: str) -> None:
        await self._repository.delete_by_id_and_user_id(tag_id, user_id)

    async def get_user_tags(self, user_id: str) -> List[Tag]:
        return await self._repository.filter_by(user_id=user_id)