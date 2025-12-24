"""
Модуль для работы с реферальной системой.
"""

from __future__ import annotations

import secrets
import string
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from backend_client import BackendClient


def generate_referral_code(length: int = 8) -> str:
    """Генерация псевдоуникального реферального кода вида 7C56AHwF."""
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_invite_link(bot_username: str, referral_code: str) -> str:
    """
    Генерирует deep-link для приглашения в бота.

    Ссылка: https://t.me/<BOT_USERNAME>?start=<referral_code>
    """
    username = bot_username.strip()
    if not username:
        raise RuntimeError("bot_username пуст")
    return f"https://t.me/{username}?start={referral_code}"


async def get_referrer_id_by_code(
    client: "BackendClient",
    referral_code: str,
) -> Optional[int]:
    """
    Возвращает id пользователя по его реферальному коду.
    Возвращает None если не найден или backend недоступен.
    """
    if not referral_code:
        return None

    resp = await client.get("/users", params={"referral_code": referral_code}, safe=True)
    if resp is None or resp.status_code != 200:
        return None

    users = resp.json().get("data") or []
    return users[0].get("id") if users else None
