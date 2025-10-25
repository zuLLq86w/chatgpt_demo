from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, and_, desc, func
from typing import Callable, Iterator, List, Optional, Tuple

from app.models import Message
from .base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, Message)

    async def get_content_by_con_id(self, con_id: str) -> List[str]:
        async with self.session_factory() as session:
            subquery = (
                select(self.model.content, self.model.create_date)
                .where(self.model.conversation_id == con_id)
                .where(self.model.status == "ok")
                .order_by(desc(self.model.create_date))
                .limit(9).offset(0)
            ).subquery()
            query = select(subquery.c.content).order_by(subquery.c.create_date)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_messages_by_con_id(self, con_id: str, limit: int, offset: int) -> Tuple[int, List[Message]]:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .where(self.model.conversation_id == con_id)
                .order_by(desc(self.model.create_date))
            )
            total_query = select(func.count()).select_from(query)
            data_query = query.limit(limit).offset(offset)
            total = await session.execute(total_query)
            data = await session.execute(data_query)
            return total.first()[0], data.scalars().all()
