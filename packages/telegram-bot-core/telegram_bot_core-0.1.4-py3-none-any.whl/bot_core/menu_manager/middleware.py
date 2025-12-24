from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from .manager import FSMMenuManager


class MenuManagerMiddleware(BaseMiddleware):
    """
    Middleware, которая прокидывает экземпляр FSMMenuManager во все хендлеры.

    Как работает:
    - При инициализации принимает уже созданный FSMMenuManager (например, из BotApp).
    - На каждом апдейте добавляет его в словарь data, который aiogram передаёт в хендлер.
    - В хендлере достаточно добавить аргумент menu_manager: FSMMenuManager,
      и aiogram автоматически подставит туда объект из data.
    """

    def __init__(self, menu_manager: FSMMenuManager) -> None:
        self._menu_manager = menu_manager

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Вызывается aiogram для каждого апдейта.

        - handler — целевой хендлер (функция, которая будет обрабатывать апдейт).
        - event   — объект апдейта (Message, CallbackQuery и т.п.).
        - data    — контекст, общий для middleware и хендлера.

        Мы просто кладём menu_manager в data и передаём исполнение дальше.
        """
        data["menu_manager"] = self._menu_manager
        return await handler(event, data)


