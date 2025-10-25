from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Callable, Iterator, List, Optional, Tuple

from app.models import Conversation, ConversationTagRel
from .base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, Conversation)

    async def get_by_user(self, user_id: str, limit: int = 10, offset: int = 0, tag_ids: List[str] = None) -> Tuple[int, List[Conversation]]:
        async with self.session_factory() as session:
            query = (
                select(Conversation)
                .join(ConversationTagRel)
                .options(joinedload(Conversation.tags))
                .where(
                    Conversation.user_id == user_id,
                    Conversation.is_group == False
                )
            )
            if tag_ids:
                query = query.where(ConversationTagRel.tag_id.in_(tag_ids))
            total_query = select(func.count()).select_from(query.subquery())
            limit_query = (query.limit(limit).offset(offset))

            total_rows = await session.execute(total_query)
            limit_rows = await session.execute(limit_query)
            total = total_rows.first()[0]
            data = limit_rows.unique().scalars().all()
            return total, data


class ConversationTagRelRepository(BaseRepository[ConversationTagRel]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, ConversationTagRel)

