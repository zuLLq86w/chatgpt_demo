from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_
from typing import Callable, Iterator, List, Optional, Tuple

from app.models import Tag
from .base import BaseRepository


class TagRepository(BaseRepository[Tag]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, Tag)

    async def delete_by_id_and_user_id(self, id: str, user_id: str) -> None:
        async with self.session_factory() as session:
            stmt = (
                delete(self.model)
                .where(self.model.id == id)
                .where(self.model.user_id == user_id)
            )
            await session.execute(stmt)
