"""
Модуль для работы с backend API.

Содержит:
- BackendError — исключение для ошибок backend
- BackendClient — обёртка над httpx.AsyncClient с обработкой ошибок
"""

from __future__ import annotations

from typing import Any, Dict, Optional

import httpx


class BackendError(Exception):
    """Ошибка при обращении к backend."""

    def __init__(self, message: str, cause: Exception | None = None):
        super().__init__(message)
        self.cause = cause


class BackendClient:
    """
    Обёртка над httpx.AsyncClient с обработкой ошибок.

    Пример использования:
        client = BackendClient("http://127.0.0.1:8000")

        # Обычный запрос — выбрасывает BackendError при ошибке сети
        resp = await client.get("/users")

        # Безопасный запрос — возвращает None при ошибке
        resp = await client.get("/users", safe=True)
    """

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        self._base_url = base_url
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout)

    @property
    def base_url(self) -> str:
        return self._base_url

    def _format_error(self, exc: Exception) -> str:
        """Форматирует ошибку в читаемое сообщение."""
        url = f" ({self._base_url})" if self._base_url else ""

        if isinstance(exc, httpx.ConnectError):
            return f"❌ Backend недоступен{url}"
        if isinstance(exc, httpx.ReadError):
            return "❌ Backend оборвал соединение"
        if isinstance(exc, httpx.TimeoutException):
            return f"❌ Backend не ответил вовремя{url}"
        return f"❌ Ошибка backend: {type(exc).__name__}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        safe: bool = False,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Optional[httpx.Response]:
        """
        Универсальный метод запроса.

        :param method: HTTP метод (GET, POST, PATCH, DELETE)
        :param path: путь API
        :param safe: если True — вернёт None при ошибке, иначе выбросит BackendError
        :param params: query-параметры
        :param json: тело запроса
        """
        try:
            return await self._client.request(method, path, params=params, json=json)
        except httpx.HTTPError as exc:
            if safe:
                return None
            raise BackendError(self._format_error(exc), cause=exc)

    # === HTTP методы ===

    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        *,
        safe: bool = False,
    ) -> Optional[httpx.Response]:
        """GET-запрос. safe=True — вернёт None при ошибке."""
        return await self._request("GET", path, params=params, safe=safe)

    async def post(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        *,
        safe: bool = False,
    ) -> Optional[httpx.Response]:
        """POST-запрос. safe=True — вернёт None при ошибке."""
        return await self._request("POST", path, json=json, safe=safe)

    async def patch(
        self,
        path: str,
        json: Optional[Dict[str, Any]] = None,
        *,
        safe: bool = False,
    ) -> Optional[httpx.Response]:
        """PATCH-запрос. safe=True — вернёт None при ошибке."""
        return await self._request("PATCH", path, json=json, safe=safe)

    async def delete(
        self,
        path: str,
        *,
        safe: bool = False,
    ) -> Optional[httpx.Response]:
        """DELETE-запрос. safe=True — вернёт None при ошибке."""
        return await self._request("DELETE", path, safe=safe)
