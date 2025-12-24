from abc import ABC, abstractmethod
from typing import Dict, Optional
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.state import State

class BaseMenu(ABC):
    def __init__(self, state: State):
        self.state = state
    
    @abstractmethod
    async def get_text(self, data: Dict) -> str:
        pass
    
    @abstractmethod
    def get_keyboard(self, data: Dict) -> Optional[InlineKeyboardMarkup]:
        pass