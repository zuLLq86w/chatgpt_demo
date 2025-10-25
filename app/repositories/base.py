import datetime
from contextlib import AbstractAsyncContextManager
from typing import (
    Generic,
    TypeVar,
    Type,
    Callable,
    Iterator,
    Optional,
    Any,
    Sequence,
    List,
    Tuple,
    Union,
    Dict,
)

import sqlalchemy
from sqlalchemy import (
    select,
    insert,
    update,
    func,
    Row,
    RowMapping,
    ScalarResult,
    and_,
    delete,
)
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
# from app.schemas import DefaultPageParams
from app.models import Base
from fastapi.encoders import jsonable_encoder

# 定义一个泛型变量，用来表示模型的类型
T = TypeVar("T", bound=Base)
# PageParams = TypeVar("PageParams", bound=DefaultPageParams)


class BaseRepository(Generic[T]):
    def __init__(
        self,
        session_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        model: Type[T],
    ) -> None:
        self.session_factory = session_factory
        self.model = model

    async def get(
        self
    ) -> List[T]:

        async with self.session_factory() as session:
            query = select(self.model)
            rows = await session.execute(query)
            return rows.scalars().all()

    async def filter_by(self, **kwargs) -> List[T]:
        async with self.session_factory() as session:
            stmt = select(self.model).filter_by(**kwargs)
            rows = await session.execute(stmt)
            return rows.scalars().all()

    async def get_by_id(self, id: str) -> Optional[T]:
        async with self.session_factory() as session:
            stmt = select(self.model).where(self.model.id == id)
            rows = await session.execute(stmt)
            return rows.scalar_one_or_none()

    async def create(self, obj: Union[T, List[T]]):
        async with self.session_factory() as session:
            if not isinstance(obj, list):
                obj = [obj]
            data = [i.to_dict() for i in obj]
            stmt = insert(self.model).values(data)
            await session.execute(stmt)

    async def update(self, id, obj: Union[T, BaseModel, Dict[str, Any]]):
        obj = jsonable_encoder(obj, exclude_none=True)

        async with self.session_factory() as session:
            stmt = update(self.model).values(**obj).where(self.model.id == id)
            await session.execute(stmt)
            return None

    async def delete(self, id: str) -> None:
        async with self.session_factory() as session:
            stmt = (
                delete(self.model)
                .where(self.model.id == id)
            )
            await session.execute(stmt)

    # async def get_list(
    #     self, params: PageParams, exclude_deleted: bool = True
    # ) -> Tuple[int, List[T]]:
    #     """
    #     获取列表
    #     Args:
    #         params: 筛选条件
    #         exclude_deleted: 是否排除已删除的数据, 默认排除
    #
    #     Returns:
    #         total: 总数量
    #         data: 数据
    #
    #     """
    #     order_func = getattr(sqlalchemy, params.sort_order)
    #     async with self.session_factory() as session:
    #         query = select(self.model)
    #
    #         filters = []
    #         for key, value in params.model_dump_without_empty().items():
    #             if hasattr(self.model, key):
    #                 filters.append(getattr(self.model, key) == value)
    #
    #         if exclude_deleted:
    #             if hasattr(self.model, "is_deleted"):
    #                 filters.append(
    #                     getattr(self.model, "is_deleted") == False
    #                 )  # 排除已删除的数据
    #
    #         if filters:
    #             query = query.where(and_(*filters))
    #
    #         total_query = select(func.count()).select_from(query.subquery())
    #         data_query = (
    #             query.order_by(order_func(getattr(self.model, params.sort_by)))
    #             .limit(params.limit)
    #             .offset(params.offset)
    #         )
    #
    #         total_rows = await session.execute(total_query)
    #         data_rows = await session.execute(data_query)
    #
    #         total = total_rows.first()[0]
    #         data = data_rows.scalars().all()
    #         return total, data
