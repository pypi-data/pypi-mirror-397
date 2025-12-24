import importlib
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ENTRY_FILE = Path("src/backend/app.py")
BACKEND_ENTRY_MODULE = "backend.app"
BACKEND_APP_ATTR = "app"


def run_backend() -> None:
    """
    Запускает backend из текущего проекта.

    Строго ожидаемая структура (относительно PROJECT_ROOT / текущей директории):
    - ./src/backend/app.py (модуль backend.app с объектом FastAPI `app`)

    Настройки:
    - PROJECT_ROOT: путь к корню проекта (по умолчанию cwd)
    - BACKEND_HOST: host (по умолчанию 0.0.0.0)
    - BACKEND_PORT: port (по умолчанию 8000)
    - BACKEND_RELOAD: 1/true/yes для autoreload (по умолчанию 0)
    """
    project_root = Path(os.environ.get("PROJECT_ROOT", Path.cwd())).resolve()

    # Загружаем .env из корня проекта (если есть)
    load_dotenv(project_root / ".env")

    entry_file = (project_root / BACKEND_ENTRY_FILE).resolve()
    if not entry_file.is_file():
        raise RuntimeError(f"Файл не найден: {entry_file}")

    src_root = (project_root / "src").resolve()
    if not src_root.is_dir():
        raise RuntimeError(f"Папка src не найдена: {src_root}")

    src_root_str = str(src_root)
    if src_root_str not in sys.path:
        sys.path.insert(0, src_root_str)

    try:
        module = importlib.import_module(BACKEND_ENTRY_MODULE)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Не удалось импортировать {BACKEND_ENTRY_MODULE} из файла {entry_file}: {exc}") from exc

    app = getattr(module, BACKEND_APP_ATTR, None)
    if app is None:
        raise RuntimeError(f"В файле {entry_file} не найден объект '{BACKEND_APP_ATTR}'")

    host = (os.environ.get("BACKEND_HOST") or "0.0.0.0").strip()
    port = int((os.environ.get("BACKEND_PORT") or "8000").strip())
    reload_raw = (os.environ.get("BACKEND_RELOAD") or "0").strip().lower()
    reload_enabled = reload_raw in {"1", "true", "yes", "y"}

    # uvicorn - опциональная зависимость (extra backend), поэтому импортим здесь.
    import uvicorn  # noqa: PLC0415

    uvicorn.run(app, host=host, port=port, reload=reload_enabled)


if __name__ == "__main__":
    run_backend()


