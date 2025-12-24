from typing import Dict, List

from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message

from .base import BaseMenu

class FSMMenuManager:
    """
    Центральный менеджер для работы с меню на базе FSM (aiogram).

    Основные задачи:
    - регистрировать меню (`BaseMenu`) за конкретными состояниями FSM (`State`);
    - уметь отрисовывать меню (новым сообщением или редактированием существующего);
    - по "короткому" имени состояния (строка в callback_data) находить нужное меню
      и выполнять переход с обновлением FSM.
    """

    def __init__(self) -> None:
        """
        Создаёт пустой менеджер меню.

        После инициализации необходимо вызвать :meth:`register_menus`,
        чтобы привязать конкретные меню к состояниям FSM.
        """
        # Храним меню по самому объекту State.
        self._menus: Dict[State, BaseMenu] = {}

    def register_menus(self, menus: List[BaseMenu]) -> None:
        """
        Регистрирует несколько меню и привязывает их к состояниям FSM.

        Каждый `BaseMenu` обязан иметь атрибут `state` (обычно элемент `StatesGroup`),
        по которому меню будет находиться методом :meth:`navigate_to`.

        :param menus: список экземпляров классов, наследующихся от `BaseMenu`.
                      Например:
                      `[MainMenu(BotStates.main_menu), ChooseProgrammMenu(BotStates.choose_today_program)]`.
        """
        for menu in menus:
            self._menus[menu.state] = menu

    async def render(self, obj: Message | CallbackQuery, state: State, data: dict) -> None:
        """
        Рендерит указанное меню либо новым сообщением, либо редактированием старого.

        Поведение:
        - если `obj` — `CallbackQuery` с `message`, то редактируем существующее сообщение;
        - иначе отправляем новое сообщение (обычно, если `obj` — `Message`).
        Чтобы в одной функции все было.

        :param obj: `Message` или `CallbackQuery`, от которого нужно "ответить" пользователю;
        :param state: состояние FSM, за которым зарегистрировано меню;
        :param data: словарь с данными сессии FSM, который передаётся в `get_text` и `get_keyboard`.
        """
        menu = self._menus.get(state)
        if not menu:
            await obj.answer("❌ Меню не найдено")
            return
        text = await menu.get_text(data)
        kb = menu.get_keyboard(data)
        if isinstance(obj, CallbackQuery) and obj.message:
            await obj.message.edit_text(text, reply_markup=kb)
        else:
            await obj.answer(text, reply_markup=kb)

    def _get_short_state_name(self, state: State) -> str:
        """
        Возвращает "короткое" имя состояния без префикса класса `StatesGroup`.

        В aiogram `State.state` имеет вид `"BotStates:main_menu"`.
        Здесь мы берём только часть после двоеточия — `"main_menu"`.

        :param state: объект состояния (`aiogram.fsm.state.State`).
        :return: короткое имя состояния (часть после двоеточия).
        """
        full_name = state.state
        return full_name.split(":", maxsplit=1)[-1]

    def _find_state_by_short_name(self, target_name: str) -> State | None:
        """
        Ищет объект `State` по его короткому имени среди уже зарегистрированных меню.

        :param target_name: строка с именем состояния, например `"main_menu"` или
                            `"choose_today_program"`.
        :return: найденный `State` или `None`, если соответствующее меню не зарегистрировано.
        """
        for st in self._menus.keys():
            if self._get_short_state_name(st) == target_name:
                return st
        return None

    async def navigate_to(
        self,
        query: CallbackQuery,
        target_name: str,
        state: FSMContext,
    ) -> None:
        """
        Универсальный переход + рендер по "короткому" имени состояния.

        Типичный сценарий:
        - пользователь нажимает inline‑кнопку (например, с `callback_data="nav:main_menu"`);
        - хендлер получает `callback_data.target == "main_menu"`;
        - вызывает `navigate_to(query, "main_menu", state)`, и менеджер:
            1. Находит нужное `State` по короткому имени среди зарегистрированных меню;
            2. Вызывает `state.set_state(...)`, переключая FSM;
            3. Берёт `data = await state.get_data()` и вызывает :meth:`render`,
               чтобы перерисовать текущее сообщение под новое меню.

        :param query: объект `CallbackQuery`, пришедший при нажатии на inline‑кнопку.
        :param target_name: "короткое" имя состояния (часть после двоеточия в `State.state`).
        :param state: `FSMContext` текущего пользователя.
        """
        target_state = self._find_state_by_short_name(target_name)
        if target_state is None:
            await query.answer("❌ Меню не найдено")
            return

        await state.set_state(target_state)
        data = await state.get_data()
        await self.render(query, target_state, data)
