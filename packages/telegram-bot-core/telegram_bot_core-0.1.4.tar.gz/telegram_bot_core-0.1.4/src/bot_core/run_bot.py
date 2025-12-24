import asyncio
import importlib
import os
import sys
from inspect import iscoroutinefunction
from pathlib import Path

from dotenv import load_dotenv

# Фолбэк-точки входа, если авто-детект по файлам не нашёл ничего подходящего.
FALLBACK_ENTRY_MODULES = ("bot.main", "app.bot.main", "main", "app.main")

def _add_to_syspath(path: Path) -> None:
    p = str(path.resolve())
    if p not in sys.path:
        sys.path.insert(0, p)


def _discover_src_roots(project_root: Path) -> list[Path]:
    """
    Находит папки src, которые нужно добавить в sys.path.

    Поддерживаем случаи, когда PROJECT_ROOT указывает на общий корень (/app),
    а сам проект лежит глубже, например:
      /app/erik_vitamin_bot/src/bot/main.py
    """
    roots: list[Path] = []

    direct = (project_root / "src").resolve()
    if direct.is_dir():
        roots.append(direct)

    # Ищем вложенные <something>/src/bot/main.py, но без rglob (он может быть дорогим на больших деревьях).
    ignored_dirnames = {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        "build",
        "dist",
        "site-packages",
    }

    def walk_dirs(base: Path, depth: int) -> list[Path]:
        if depth <= 0:
            return []
        out: list[Path] = []
        try:
            for p in base.iterdir():
                if not p.is_dir():
                    continue
                if p.name in ignored_dirnames:
                    continue
                out.append(p)
                out.extend(walk_dirs(p, depth - 1))
        except OSError:
            return out
        return out

    # Обычно проект лежит на 1 уровень глубже (/app/<project>/src/...), но дадим запас до 2.
    for candidate_root in walk_dirs(project_root, depth=2):
        entry = candidate_root / "src" / "bot" / "main.py"
        if entry.is_file():
            roots.append((candidate_root / "src").resolve())

    # Уникализируем и сортируем детерминированно: ближе к корню — выше приоритет.
    uniq: dict[str, Path] = {str(p): p for p in roots}
    return sorted(uniq.values(), key=lambda p: (len(p.parts), str(p)))


def _discover_entry_modules(project_root: Path) -> tuple[str, ...]:
    """
    Пытаемся угадать точку входа по наличию файлов.

    Поддерживаем популярные layout'ы:
    - src-layout:  ./src/<package>/...
    - flat-layout: ./<package>/...
    """
    candidates: list[str] = []

    # Проверяем сначала src-layout, затем flat-layout.
    bases = [project_root / "src", project_root]
    for base in bases:
        if not base.is_dir():
            continue

        # Самые частые варианты.
        if (base / "bot" / "main.py").is_file():
            candidates.append("bot.main")
        if (base / "app" / "bot" / "main.py").is_file():
            candidates.append("app.bot.main")

        # Более общий "main.py" в корне package/проекта.
        if (base / "main.py").is_file():
            candidates.append("main")
        if (base / "app" / "main.py").is_file():
            candidates.append("app.main")

    # Удаляем дубликаты, сохраняя порядок.
    unique: list[str] = []
    seen: set[str] = set()
    for m in candidates:
        if m in seen:
            continue
        seen.add(m)
        unique.append(m)

    return tuple(unique)


def run_bot() -> None:
    """
    Запускает бота из ТЕКУЩЕГО репозитория.

    Ожидаемая структура проекта:
    - ./src/bot/main.py  (package "bot" с async main())

    Настройки (env):
    - PROJECT_ROOT: путь к корню проекта (по умолчанию текущая директория)
    """
    project_root = Path(os.environ.get("PROJECT_ROOT", Path.cwd())).resolve()

    # Загружаем .env из корня проекта (если есть)
    load_dotenv(project_root / ".env")

    # Даем импортам видеть код проекта.
    # Поддерживаем оба популярных layout'а:
    # - "src layout":  ./src/<package>/...
    # - "flat layout": ./<package>/...
    _add_to_syspath(project_root)

    # Для src-layout добавляем ./src. Если PROJECT_ROOT указывает на "супер-корень" (например /app),
    # то также пытаемся найти вложенный .../src где лежит bot/main.py.
    for src_root in _discover_src_roots(project_root):
        _add_to_syspath(src_root)

    entry_modules = _discover_entry_modules(project_root)
    if not entry_modules:
        entry_modules = FALLBACK_ENTRY_MODULES

    last_exc: Exception | None = None
    module = None
    module_name = None
    for name in entry_modules:
        if not name:
            continue
        try:
            module = importlib.import_module(name)
            module_name = name
            main_func = getattr(module, "main", None)
            if callable(main_func) and iscoroutinefunction(main_func):
                break

            # Не подходит — пробуем следующий.
            module = None
            module_name = None
            last_exc = RuntimeError(f"Module {name} does not expose async main()")
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            continue

    if module is None or module_name is None:
        tried = ", ".join(m for m in entry_modules if m)
        hint = f" (last error: {last_exc})" if last_exc else ""
        raise RuntimeError(
            "Entry module not found / failed to import.\n"
            f"Tried: {tried}\n"
            f"PROJECT_ROOT={project_root}\n"
            "Expected file like: ./src/bot/main.py (src-layout) OR ./bot/main.py (flat-layout) with async main().\n"
            "If your project is nested (e.g. ./erik_vitamin_bot/src/bot/main.py), set PROJECT_ROOT accordingly."
            f"{hint}"
        )

    # module_name найден и main() уже проверен как async.
    asyncio.run(module.main())


if __name__ == "__main__":
    run_bot()
