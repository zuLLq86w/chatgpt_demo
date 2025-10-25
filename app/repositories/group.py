from contextlib import AbstractAsyncContextManager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import Callable, Iterator, List, Optional, Tuple

from app.models import Group, GroupRobot, GroupMember, GroupRobotRel
from .base import BaseRepository
from loguru import logger


class GroupRobotRepository(BaseRepository[GroupRobot]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, GroupRobot)

    async def get_robots_by_group_id(self, group_id: str):
        async with self.session_factory() as session:
            query = (select(
                self.model.id, self.model.name, self.model.personality, GroupRobotRel.weight, self.model.keywords
            ).join(GroupRobotRel
                   ).where(GroupRobotRel.group_id == group_id)).order_by(GroupRobotRel.weight)


            result = await session.execute(query)
            return result.mappings().all()



class GroupRepository(BaseRepository[Group]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, Group)

    async def get_list(self, user_id: str) -> List[Group]:
        async with self.session_factory() as session:
            query = select(self.model).join(GroupMember).where(GroupMember.user_id==user_id)
            result = await session.execute(query)
            return result.scalars().all()

    async def get_detail(self, group_id: str) -> Optional[Group]:
        async with self.session_factory() as session:
            query = (
                select(self.model)
                .options(
                    selectinload(self.model.members).selectinload(GroupMember.user),
                    selectinload(self.model.robots).selectinload(GroupRobotRel.robot),
                )
                .where(self.model.id == group_id)
            )
            result = await session.execute(query)
            logger.info(result)
            return result.scalar_one_or_none()


class GroupMemberRepository(BaseRepository[GroupMember]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, GroupMember)


class GroupRobotRelRepository(BaseRepository[GroupRobotRel]):
    def __init__(self, session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]]) -> None:
        super().__init__(session_factory, GroupRobotRel)
