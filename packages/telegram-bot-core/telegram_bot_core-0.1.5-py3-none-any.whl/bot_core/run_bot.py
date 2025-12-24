import asyncio
import importlib
import os
import sys
from inspect import iscoroutinefunction
from pathlib import Path

from dotenv import load_dotenv


BOT_ENTRY_FILE = Path("src/bot/main.py")
BOT_ENTRY_MODULE = "bot.main"


def run_bot() -> None:
    """
    Запускает бота из текущего проекта.

    Строго ожидаемая структура (относительно PROJECT_ROOT / текущей директории):
    - ./src/bot/main.py  (модуль bot.main с async main())

    Настройки:
    - PROJECT_ROOT: путь к корню проекта (по умолчанию cwd)
    """
    project_root = Path(os.environ.get("PROJECT_ROOT", Path.cwd())).resolve()

    # Загружаем .env из корня проекта (если есть)
    load_dotenv(project_root / ".env")

    entry_file = (project_root / BOT_ENTRY_FILE).resolve()
    if not entry_file.is_file():
        raise RuntimeError(f"Файл не найден: {entry_file}")

    src_root = (project_root / "src").resolve()
    if not src_root.is_dir():
        raise RuntimeError(f"Папка src не найдена: {src_root}")

    src_root_str = str(src_root)
    if src_root_str not in sys.path:
        sys.path.insert(0, src_root_str)

    try:
        module = importlib.import_module(BOT_ENTRY_MODULE)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Не удалось импортировать {BOT_ENTRY_MODULE} из файла {entry_file}: {exc}") from exc

    main_func = getattr(module, "main", None)
    if not callable(main_func):
        raise RuntimeError(f"В файле {entry_file} не найден async main() (атрибут main отсутствует)")
    if not iscoroutinefunction(main_func):
        raise RuntimeError(f"В файле {entry_file} не найден async main() (main не async)")

    asyncio.run(main_func())


if __name__ == "__main__":
    run_bot()
