from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Общий Base для всех backend-моделей.

    Наследуйтесь от него в общих моделях (например, User) и в моделях конкретных ботов,
    если хотите использовать общую инфраструктуру миграций/создания схемы.
    """

    pass


def create_db_connection(database_url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    """
    Создаёт подключение к БД: engine и фабрику сессий.

    Параметры:
        database_url: строка подключения к БД (например, postgresql+asyncpg://...).

    Возвращает:
        Кортеж (engine, session_factory).

    Пример:
        engine, AsyncSessionLocal = create_db_connection(database_url)
    """
    engine = create_async_engine(database_url, echo=False, future=True)
    session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return engine, session_factory

