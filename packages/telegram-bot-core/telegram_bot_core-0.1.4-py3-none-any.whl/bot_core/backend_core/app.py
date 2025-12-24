from __future__ import annotations

import time
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Callable, Dict

from aiogram.types.update import Update
from fastapi import Depends, FastAPI, Request
from fastcrud import crud_router
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.routing import BaseRoute

from src.bot_core.base_bot import BotApp

from .db import Base
from .models import BotSettings, User


def _is_system_endpoint(route: BaseRoute) -> bool:
    """
    Фильтр для скрытия системных эндпоинтов FastAPI/Swagger при логировании.
    """
    if (
        route.path.startswith(("/docs", "/openapi", "/redoc"))
        or route.name in ("root", "swagger_ui_html", "redoc_html")
        or ("HEAD" in getattr(route, "methods", set()) and len(route.methods) == 2)
    ):
        return True
    return False


def create_backend_app(
    *,
    async_session_factory: async_sessionmaker[AsyncSession],
    engine,
    title: str = "bot backend",
) -> FastAPI:
    """
    Фабрика FastAPI-приложения для backend'а бота.

    На вход получает:
    - async_session_factory — фабрику AsyncSession (обычно AsyncSessionLocal),
    - engine                — AsyncEngine для создания таблиц,
    - title                 — заголовок приложения.

    Внутри:
    - создаёт lifespan, который поднимает схему БД и логирует эндпоинты;
    - настраивает middleware для измерения времени запросов;
    - поднимает CRUD-роутер для модели User через fastcrud;
    - добавляет ручку /raw_user/{username} для отладки.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Создаём таблицы при старте приложения.
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        # 🚀 Выводим список эндпоинтов (кроме системных).
        print("\n🚀 Эндпоинты: ")
        print("-" * 50)
        for route in app.routes:
            if _is_system_endpoint(route):
                continue
            methods = ",".join(getattr(route, "methods", []))
            print(f"  {methods} {route.path}")
        print("-" * 50)

        yield

        # 🛑 SHUTDOWN
        print("🛑 Сервер остановлен")

    app = FastAPI(title=title, lifespan=lifespan)

    async def get_db() -> AsyncGenerator[AsyncSession, None]:
        async with async_session_factory() as session:
            yield session

    @app.middleware("http")
    async def timing_middleware(request: Request, call_next: Callable):  # type: ignore[override]
        """
        Логируем полное время обработки HTTP-запросов backend'ом.
        """
        started_at = time.perf_counter()
        response = await call_next(request)
        total_ms = (time.perf_counter() - started_at) * 1000
        print(f"[backend] {request.method} {request.url.path} total={total_ms:.1f} ms")
        return response

    class UserSchema(BaseModel):
        """
        Схема пользователя для CRUD-эндпоинтов.

        Используется и для создания, и для обновления.
        """

        username: str | None = None
        is_admin: bool = False
        referral_code: str | None = None
        current_state: str | None = None
        fsm_data: dict | None = None
        is_blocked: bool = False
        referrer_id: int | None = None

        class Config:
            from_attributes = True

    class BotSettingsSchema(BaseModel):
        """
        Схема настроек бота.

        Ожидается ровно одна запись в таблице bot_settings, которую мы будем
        читать/обновлять через CRUD-эндпоинты.
        """

        is_technical_work: bool = False
        technical_working_text: str | None = None
        blocked_user_text: str | None = None

        class Config:
            from_attributes = True

    # Автоматически сгенерированные CRUD-эндпоинты для User (по id)
    user_router = crud_router(
        session=get_db,
        model=User,
        create_schema=UserSchema,
        update_schema=UserSchema,
        path="/users",
        tags=["users"],
    )
    app.include_router(user_router)

    # CRUD-эндпоинты для BotSettings
    settings_router = crud_router(
        session=get_db,
        model=BotSettings,
        create_schema=BotSettingsSchema,
        update_schema=BotSettingsSchema,
        path="/settings",
        tags=["settings"],
    )
    app.include_router(settings_router)



    @app.post("/webhook")
    async def telegram_webhook(request: Request) -> Dict[str, bool]:
        """
        Точка входа для Telegram webhook'а.

        Ожидается, что BotApp уже инициализирован, и его Dispatcher доступен
        через BotApp._instance.bot.
        """
        bot = BotApp._instance.bot
        update = Update.model_validate(await request.json())
        await bot.dp.feed_update(bot, update)
        return {"ok": True}

    return app


