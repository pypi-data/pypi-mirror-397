import os
from pathlib import Path

import uvicorn

from dotenv import load_dotenv


def run_backend() -> None:
    """
    Запускает backend из ТЕКУЩЕГО репозитория.

    Ожидаемая структура проекта:
    - ./src/backend/app.py (package "backend", объект FastAPI "app")

    Настройки (env):
    - PROJECT_ROOT: путь к корню проекта (по умолчанию текущая директория)
    - BACKEND_APP: путь импорта uvicorn, по умолчанию "backend.app:app"
    """
    project_root = Path(os.environ.get("PROJECT_ROOT", Path.cwd())).resolve()

    # Загружаем .env из корня проекта (если есть)
    load_dotenv(project_root / ".env")

    app_import_path = (os.environ.get("BACKEND_APP") or "src.backend.app:app").strip()

    uvicorn.run(
        app_import_path,
        host="0.0.0.0", port=8000,
        reload=True,
    )


if __name__ == "__main__":
    run_backend()


