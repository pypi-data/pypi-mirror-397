import re

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from menu_manager.manager import FSMMenuManager


# Универсальный роутер для навигации по меню через callback_data вида "GOTO-<state_name>".
# Подключается в BotApp через dp.include_router(base_router.router).
router = Router()

_GOTO_PATTERN = re.compile(r"^GOTO-(?P<target>[A-Za-z0-9_]+)$")


@router.callback_query(F.data.regexp(_GOTO_PATTERN))
async def goto_menu_handler(
    query: CallbackQuery,
    state: FSMContext,
    menu_manager: FSMMenuManager,
) -> None:
    """
    Универсальный переход между меню по callback_data вида "GOTO-<state_name>".

    Примеры callback_data:
    - "GOTO-main_menu"
    - "GOTO-choose_today_program"
    - "GOTO-choose_today_calories"

    Где <state_name> — это "короткое имя" состояния (часть после двоеточия в State.state),
    с которым работает FSMMenuManager.
    """
    raw = query.data or ""
    match = _GOTO_PATTERN.match(raw)
    if not match:
        await query.answer("❌ Некорректный формат GOTO")
        return

    target = match.group("target")
    await menu_manager.navigate_to(query, target, state)
    await query.answer()

