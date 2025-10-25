from asyncio import current_task
from contextlib import asynccontextmanager, AbstractAsyncContextManager
from contextvars import ContextVar
from fastapi import HTTPException
from typing import Callable

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_scoped_session,
)
from sqlalchemy.orm import sessionmaker
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from pymysql.err import MySQLError

session_var = ContextVar("session_var", default=None)


class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url,
            echo=False,  # 是否打印sql, 已通过loguru接管日志配置
            pool_size=10,  # 连接池大小
            max_overflow=20,  # 连接池最大溢出数量
            pool_pre_ping=True,
            pool_timeout=30,  # 获取连接的超时时间, 应小于mysql中的wait_timeout
            pool_recycle=3600,  # 连接池回收时间, 应小于mysql中的wait_timeout or interactive_timeout
        )
        self._session_factory = async_scoped_session(
            sessionmaker(
                bind=self._engine, class_=AsyncSession, expire_on_commit=False
            ),
            current_task,
        )

    @asynccontextmanager
    async def session(self) -> Callable[..., AbstractAsyncContextManager[AsyncSession]]:
        session: AsyncSession | None = session_var.get()
        if not session:
            session: AsyncSession = self._session_factory()
            token = session_var.set(session)
            try:
                yield session

                await session.commit()
            except (SQLAlchemyError, MySQLError) as e:
                logger.exception(e)
                await session.rollback()
                raise HTTPException(status_code=500, detail="Internal Server Error")
            finally:
                await session.close()
                session_var.reset(token)
        else:
            yield session
