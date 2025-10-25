from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Callable, Iterator, List, Optional, Tuple

from app.models import User
from .base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, User)

    async def is_exist_by_username(self, username: str) -> bool:
        async with self.session_factory() as session:
            query = select(self.model.username).where(self.model.username == username)
            rows = await session.execute(query)
            return rows.scalar_one_or_none() is not None

    async def get_by_username(self, username: str) -> Optional[User]:
        async with self.session_factory() as session:
            query = select(self.model).where(self.model.username == username)
            rows = await session.execute(query)
            return rows.scalar_one_or_none()
