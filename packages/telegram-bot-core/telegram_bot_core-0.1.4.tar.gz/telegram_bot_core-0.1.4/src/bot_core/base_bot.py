import asyncio
import os
import importlib
import pathlib
import pkgutil
from typing import Optional

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseStorage
from aiogram.fsm.storage.memory import MemoryStorage

from menu_manager.manager import FSMMenuManager
from menu_manager.middleware import MenuManagerMiddleware
from base_handler import base_router
from bot_middlewares.middleware import BackendStateMiddleware

WEBHOOK_PATH = "/webhook" # ФИКСИРОВАННЫЙ РОУТ для webhook

class BotApp:
    """
    Обёртка над aiogram Bot/Dispatcher для унификации запуска ботов.

    - Автоматически подключает все роутеры из указанного пакета handlers.
    - Логирует в консоль сообщение "Бот <BOT_NAME> запущен" после старта polling.
    - Позволяет выбрать хранилище FSM: по умолчанию MemoryStorage или явное хранилище.

    Если нужно использовать не in‑memory FSM, а, например, PostgreSQL:

    1. Реализуйте своё хранилище, совместимое с BaseStorage (PostgresStorage),
       которое внутри создаёт подключение к БД по DSN.
    2. Создайте экземпляр этого хранилища и передайте его в BotApp через параметр storage.

    """

    _instance = None  # 🆕 Singleton

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(
        self,
        *,
        token: str,
        handlers_pkg: str,
        bot_name_env: str = "BOT_NAME",
        storage: Optional[BaseStorage] = None,
        backend_url: Optional[str] = None,
        use_web_hook: bool = False
    ) -> None:
        self.use_web_hook = use_web_hook
        self._token = token
        self._handlers_pkg = handlers_pkg
        self._bot_name_env = bot_name_env
        self._storage_override = storage
        self._backend_url = backend_url
        self.bot = None
        self.menu_manager = FSMMenuManager()

    def _build_storage(self) -> BaseStorage:
        """
        Возвращает экземпляр хранилища для FSM.

        - Если передано явное storage — используется оно (например, Redis/БД‑storage).
        - По умолчанию — MemoryStorage.
        """
        if self._storage_override is not None:
            return self._storage_override

        return MemoryStorage()

    def _include_all_routers(self, dp: Dispatcher) -> None:
        """
        Динамически находит и подключает все роутеры из пакета handlers.

        Ожидается, что handlers_pkg указывает на пакет, содержащий подмодули с router:
        например, 'src.bots.egor_manager_bot.bot.handlers'.
        """
        pkg = importlib.import_module(self._handlers_pkg)
        pkg_path = pathlib.Path(pkg.__file__).parent

        for module_info in pkgutil.walk_packages(
            [str(pkg_path)], prefix=f"{self._handlers_pkg}."
        ):
            mod = importlib.import_module(module_info.name)
            router = getattr(mod, "router", None)
            if router is not None:
                dp.include_router(router)
    
    async def check_webhook(bot: Bot) -> Optional[str]:
        """Проверяет webhook и возвращает URL если настроен"""
        webhook_info = await bot.get_webhook_info()
        return webhook_info.url

    async def run(self) -> None:
        """Создаёт Bot/Dispatcher, подключает роутеры и запускает polling."""
        bot = Bot(token=self._token)
        dp = Dispatcher(storage=self._build_storage())

        # Подключаем middleware, которая прокидывает menu_manager во все хендлеры.
        # Благодаря этому любой хендлер может принять аргумент menu_manager: FSMMenuManager
        # и работать с уже инициализированным менеджером меню из BotApp.
        dp.update.outer_middleware(MenuManagerMiddleware(self.menu_manager))

        # Если у бота есть backend, синхронизируем FSM-состояние с ним.
        # Это позволяет после рестарта бота восстановить состояние диалога
        # из поля current_state в таблице users.
        if self._backend_url:
            dp.update.outer_middleware(BackendStateMiddleware(self._backend_url))

        # Подключаем универсальный роутер для обработки большинйства callbacks.
        # Остальные будут подключаться автоматически через _include_all_routers.
        dp.include_router(base_router.router)

        self._include_all_routers(dp)

        async def _on_startup() -> None:  # noqa: ARG001
            bot_name = os.environ.get(self._bot_name_env, "unknown")
            print(f"Бот {bot_name} запущен")
        dp.startup.register(_on_startup)
        self.bot = bot



        if self.use_web_hook == True:
            # 2. WEBHOOK: Backend шлёт updates → dp.feed_update()
            print("🌐 Backend → dp.feed_update()")
            while True:  # 3. Держим ЖИВЫМ!
                await asyncio.sleep(3600)
        else:
            await dp.start_polling(bot)
            
        
        



