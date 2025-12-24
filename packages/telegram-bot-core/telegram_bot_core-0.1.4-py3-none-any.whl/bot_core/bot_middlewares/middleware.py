from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Optional, Tuple

import httpx
from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import TelegramObject

"""
Модуль для интеграции FSM-состояния бота с backend'ом.

Содержит middleware, которая:
- подтягивает состояние пользователя и FSM-данные из backend'а при первом апдейте;
- записывает новое состояние и данные в backend при каждом изменении FSM.
"""


class BackendStateMiddleware(BaseMiddleware):
    """
    Middleware для синхронизации FSM-состояния и FSM-данных пользователя с backend'ом.

    Задачи:
    - При первом апдейте после старта бота, если локальное состояние пустое,
      подтянуть current_state и fsm_data из backend'а.
    - При каждом изменении FSM-состояния или данных отправлять PATCH в backend.
    - Проверять режим технических работ (BotSettings.is_technical_work).
    - Проверять блокировку пользователя (User.is_blocked).

    Ожидается, что backend реализует следующие эндпоинты:
    - GET /users?username=<username> -> {"data": [{"id", "current_state", "fsm_data", ...}]}
    - PATCH /users/{id} с json {"current_state": "...", "fsm_data": {...}}
    - GET /settings -> {"data": [{"is_technical_work", "technical_working_text", ...}]}
    """

    def __init__(self, backend_base_url: str) -> None:
        """
        Инициализирует middleware с HTTP-клиентом для общения с backend'ом.

        Параметры:
        - backend_base_url: базовый URL backend-сервера,
          например "http://127.0.0.1:8000".
        """
        self._client = httpx.AsyncClient(base_url=backend_base_url, timeout=5.0)

    async def _save_fsm_to_backend(
        self,
        user_id: int,
        current_state: Optional[str],
        fsm_data: Optional[Dict[str, Any]],
    ) -> None:
        """
        Сохраняет FSM-состояние и данные пользователя в backend.

        Параметры:
        - user_id: ID пользователя в БД (не Telegram ID).
        - current_state: строка состояния FSM (например "BotStates:main_menu").
        - fsm_data: словарь с FSM-данными.
        """
        try:
            await self._client.patch(
                f"/users/{user_id}",
                json={
                    "current_state": current_state,
                    "fsm_data": fsm_data,
                },
            )
        except httpx.HTTPError:
            # Backend недоступен — тихо игнорируем, чтобы не ломать бота
            pass

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Основной хук middleware.

        Последовательность:
        0. Проверяем технические работы и блокировку пользователя.
        1. Читаем текущее локальное FSM-состояние и данные.
        2. Если локальное состояние пустое — подтягиваем из backend.
        3. Передаём управление следующему хендлеру.
        4. Сравниваем состояние/данные до и после.
        5. Если что-то изменилось — сохраняем в backend.
        """
        state: FSMContext = data["state"]
        from_user = data.get("event_from_user")
        username = (from_user.username or "").strip() if from_user else None

        # === 0. Проверяем настройки бота (технические работы) ===
        blocked_user_text: str = "Вы заблокированы в боте."

        try:
            settings_resp = await self._client.get("/settings")
        except httpx.HTTPError:
            settings_resp = None

        if settings_resp is not None and settings_resp.status_code == 200:
            settings_body = settings_resp.json()
            settings_items = settings_body.get("data") or []
            if settings_items:
                settings = settings_items[0]
                is_technical_work = bool(settings.get("is_technical_work"))
                technical_text = settings.get("technical_working_text") or None
                blocked_user_text = settings.get("blocked_user_text") or blocked_user_text

                if is_technical_work and from_user:
                    text = technical_text or "В боте проводятся технические работы."
                    bot = data.get("bot")
                    if bot is not None:
                        await bot.send_message(chat_id=from_user.id, text=text)
                    return

        # === 1. Получаем данные пользователя из backend ===
        user_from_backend: Optional[Dict[str, Any]] = None

        if username:
            try:
                resp = await self._client.get("/users", params={"username": username})
            except httpx.HTTPError:
                resp = None

            if resp is not None and resp.status_code == 200:
                body = resp.json()
                users = body.get("data") or []
                if users:
                    user_from_backend = users[0]

                    # Проверяем блокировку
                    is_blocked = bool(user_from_backend.get("is_blocked"))
                    if is_blocked and from_user:
                        bot = data.get("bot")
                        if bot is not None:
                            await bot.send_message(
                                chat_id=from_user.id,
                                text=blocked_user_text,
                            )
                        return

        # === 2. Читаем локальное FSM-состояние и данные ===
        old_state = await state.get_state()
        old_data = await state.get_data()

        # === 3. Если локальное состояние пустое — подтягиваем из backend ===
        if old_state is None and user_from_backend is not None:
            backend_state = user_from_backend.get("current_state")
            backend_fsm_data = user_from_backend.get("fsm_data")

            if backend_state:
                # Восстанавливаем состояние
                await state.set_state(backend_state)
                old_state = backend_state

                # Восстанавливаем данные FSM
                if isinstance(backend_fsm_data, dict) and backend_fsm_data:
                    await state.update_data(**backend_fsm_data)
                    old_data = await state.get_data()

        # === 4. Передаём управление хендлеру ===
        result = await handler(event, data)

        # === 5. Сравниваем состояние/данные и сохраняем в backend если изменились ===
        new_state = await state.get_state()
        new_data = await state.get_data()

        state_changed = new_state != old_state
        data_changed = new_data != old_data

        if (state_changed or data_changed) and user_from_backend is not None:
            user_id = user_from_backend.get("id")
            if user_id is not None:
                await self._save_fsm_to_backend(
                    user_id=user_id,
                    current_state=new_state,
                    fsm_data=new_data if new_data else None,
                )

        return result
