from __future__ import annotations

from sqlalchemy import Boolean, Column, Integer, String, JSON

from .db import Base


class User(Base):
    """
    Общая модель пользователя для backend'ов ботов.

    Таблица users:
    - id            — PK
    - username      — уникальный логин/username
    - is_admin      — флаг администратора
    - is_blocked    — флаг блокировки пользователя в боте
    - current_state — текущее FSM-состояние (строка вида "BotStates:main_menu")
    - fsm_data      — JSON с данными FSM (selectedProgramName, calorieOptions и т.п.)
    - referral_code — реферальный код
    - referrer_id   — ID пригласившего пользователя
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, index=True, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_blocked = Column(Boolean, nullable=False, default=False)
    current_state = Column(String(255), nullable=True)
    fsm_data = Column(JSON, nullable=True)
    referral_code = Column(String(32), unique=True, index=True, nullable=True)
    referrer_id = Column(Integer, nullable=True)


class BotSettings(Base):
    """
    Общие настройки бота, хранящиеся в базе backend'а.

    Таблица bot_settings:
    - id                     — PK (ожидается ровно одна запись)
    - is_technical_work      — включён ли режим технических работ
    - technical_working_text — текст, которым бот отвечает при техработах
    - blocked_user_text      — текст, которым бот отвечает заблокированным пользователям
    """

    __tablename__ = "bot_settings"

    id = Column(Integer, primary_key=True, index=True)
    is_technical_work = Column(Boolean, nullable=False, default=False)
    technical_working_text = Column(String(1024), nullable=True)
    blocked_user_text = Column(String(1024), nullable=True)


