from __future__ import annotations

import asyncio
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import httpx
import pandas as pd
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2 import service_account


SCOPES = [
    # Доступ к чтению содержимого таблиц (нужен для parts, metadata и т.п.).
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    # Нужен для перечисления доступных таблиц и экспорта файлов через Google Drive.
    "https://www.googleapis.com/auth/drive.readonly",
]


@dataclass
class PreloadedSheet:
    """
    Небольшой объект-обёртка над DataFrame с данными одного листа.

    - name  — название листа.
    - data  — pandas.DataFrame с уже обрезанным диапазоном A1:P30.
    """

    name: str
    data: pd.DataFrame


@dataclass
class PreloadedSpreadsheet:
    """
    Экземпляр предзагруженной таблицы Google Spreadsheet.

    Хранит:
    - id     — spreadsheetId из Google Drive.
    - name   — человекочитаемое имя файла в Google Drive.
    - sheets — список листов (PreloadedSheet), чтобы можно было
      обращаться к ним по индексу или имени.
    """

    id: str
    name: str
    sheets: List[PreloadedSheet]

    def __getitem__(self, index: int) -> PreloadedSheet:
        """
        Позволяет обращаться к листам по индексу:
            spreadsheet[0] -> PreloadedSheet
        """
        return self.sheets[index]

    def get_sheet(self, name: str) -> PreloadedSheet | None:
        """
        Возвращает лист по имени или None, если такого листа нет.
        """
        for sheet in self.sheets:
            if sheet.name == name:
                return sheet
        return None


class GoogleSheetsRegistry:
    """

    - Создаёт авторизацию по сервисному аккаунту (читаем JSON с диска).
    - Умеет перечислять все доступные сервисному аккаунту Google Sheets
      через Drive API (id + name).

      Нужен если хотим работать со списком google таблиц.
    """

    def __init__(self, service_account_path: Path) -> None:
        """
        service_account_path — путь к JSON ключу сервисного аккаунта
        (обычно service_account.json).
        """
        info: Dict[str, Any] = json.loads(service_account_path.read_text(encoding="utf-8"))
        self._sa_credentials = service_account.Credentials.from_service_account_info(
            info,
            scopes=SCOPES,
        )
        self._request = GoogleRequest()
        # Кэш предзагруженных таблиц, каждая со своими листами.
        # Это позволяет не скачивать и не парсить одни и те же файлы повторно.
        self._preloaded_spreadsheets: List[PreloadedSpreadsheet] = []

    def _get_access_token(self) -> str:
        """
        Получает актуальный access_token для сервисного аккаунта. Нужен для Google Drive API.
        """
        if not self._sa_credentials.valid:
            self._sa_credentials.refresh(self._request)
        return self._sa_credentials.token  # type: ignore[no-any-return]

    async def list_accessible_spreadsheets(self) -> List[Dict[str, str]]:
        """
        Возвращает список всех доступных сервисному аккаунту таблиц (id и name)
        через Google Drive API. Аналог listAccessibleSpreadsheets из NodeJS.
        """
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        results: List[Dict[str, str]] = []
        page_token: str | None = None

        async with httpx.AsyncClient(base_url="https://www.googleapis.com") as client:
            while True:
                params = {
                    "q": "mimeType='application/vnd.google-apps.spreadsheet' and trashed=false",
                    "pageSize": "1000",
                    "fields": "nextPageToken, files(id,name)",
                }
                if page_token:
                    params["pageToken"] = page_token

                resp = await client.get(
                    "/drive/v3/files", headers=headers, params=params, timeout=10.0
                )
                if resp.status_code != 200:
                    raise RuntimeError(
                        f"Drive API error: {resp.status_code} {resp.reason_phrase}"
                    )

                data = resp.json()
                files = data.get("files") or []
                results.extend(
                    {"id": f.get("id", ""), "name": f.get("name", "")}
                    for f in files
                    if f.get("id") and f.get("name")
                )

                page_token = data.get("nextPageToken")
                if not page_token:
                    break

        return results

    async def preload_all_sheets(self) -> List[PreloadedSpreadsheet]:
        """
        Предзагружает в память все доступные сервисному аккаунту Google Sheets.

        Зачем это нужно:
        - При старте бота один раз получаем список всех таблиц через Google Drive.
        - Для каждой таблицы запрашиваем экспорт в формате Excel (XLSX)
          через Drive API (`files.export`), без обращения к Sheets API.
        - Затем читаем файл в pandas и забираем только "кусок" A1:X30 для
          каждого листа (worksheet) в этой книге.

        Возвращает:
        - Список PreloadedSpreadsheet.
        - У каждой таблицы есть список листов (PreloadedSheet) с данными A1:X30.
        """
        # Если мы уже один раз всё предзагрузили в рамках жизни процесса,
        # повторный вызов просто вернёт кэш — дополнительный запрос к Google API не нужен.
        if self._preloaded_spreadsheets:
            return self._preloaded_spreadsheets

        # 1. Получаем список всех доступных таблиц через Drive API.
        spreadsheets_meta = await self.list_accessible_spreadsheets()

        # 2. Для экспорта файлов используем тот же access_token, что и для Drive.
        token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {token}",
        }

        preloaded: List[PreloadedSpreadsheet] = []

        async with httpx.AsyncClient(base_url="https://www.googleapis.com") as client:
            for meta in spreadsheets_meta:
                spreadsheet_id = meta["id"]
                spreadsheet_name = meta["name"]
                print(
                    f"Загружаю таблицу: "
                    f"{spreadsheet_name!r} (id={spreadsheet_id})"
                )

                try:
                    # Экспортируем всю книгу (все листы) в формат XLSX через Drive API.
                    resp = await client.get(
                        f"/drive/v3/files/{spreadsheet_id}/export",
                        params={
                            "mimeType": (
                                "application/vnd.openxmlformats-officedocument."
                                "spreadsheetml.sheet"
                            )
                        },
                        headers=headers,
                        timeout=60.0,
                    )
                    if resp.status_code != 200:
                        print(
                            "[GoogleSheetsRegistry] failed to export spreadsheet "
                            f"{spreadsheet_id}: {resp.status_code} {resp.reason_phrase}"
                        )
                        continue

                    # Читаем бинарное содержимое XLSX в pandas.
                    try:
                        excel_bytes = io.BytesIO(resp.content)
                        sheets_dict = pd.read_excel(
                            excel_bytes,
                            sheet_name=None,  # dict[str, DataFrame] для всех листов
                            engine="openpyxl",
                        )
                    except Exception as exc:  # noqa: BLE001
                        print(
                            "[GoogleSheetsRegistry] failed to parse XLSX for "
                            f"{spreadsheet_id}: {exc}"
                        )
                        continue

                    # Для каждого листа берём только срез A1:P30 (30 строк, 16 колонок)
                    # и собираем объект таблицы с её листами.
                    sheets: List[PreloadedSheet] = []
                    for sheet_name, df in sheets_dict.items():
                        # iloc безопасен: если строк/колонок меньше, pandas сам обрежет.
                        # 30 строк, 24 колонки (A-X) — достаточно для таблиц с 5+ калорийностями
                        chunk = df.iloc[0:30, 0:24].copy()
                        sheets.append(PreloadedSheet(name=sheet_name, data=chunk))

                    preloaded.append(
                        PreloadedSpreadsheet(
                            id=spreadsheet_id,
                            name=spreadsheet_name,
                            sheets=sheets,
                        )
                    )

                except httpx.HTTPError as exc:
                    # Любая ошибка HTTP на уровне сети/клиента — логируем и идём дальше.
                    print(
                        "[GoogleSheetsRegistry] HTTP error while exporting "
                        f"spreadsheet {spreadsheet_id}: {exc}"
                    )

        # Сохраняем кэш, чтобы повторно не дергать Google API и не парсить файлы.
        self._preloaded_spreadsheets = preloaded
        return preloaded

    def get_table_names(self) -> List[str]:
        """
        Возвращает список названий всех уже предзагруженных таблиц.

        Ожидается, что preload_all_sheets() уже был вызван ранее
        (например, при старте бота). Если кэш пуст, вернёт пустой список.
        """
        names = [spreadsheet.name for spreadsheet in self._preloaded_spreadsheets]
        print(f"[GoogleSheetsRegistry] currently preloaded tables: {names}")
        return names

    # === Вспомогательные методы для доступа к предзагруженным данным ===

    def get_spreadsheet(self, name: str) -> PreloadedSpreadsheet | None:
        """
        Возвращает предзагруженную книгу по имени файла (как в Google Drive).

        Ожидается, что preload_all_sheets() уже был вызван.
        Если книга не найдена — возвращает None.
        """
        for spreadsheet in self._preloaded_spreadsheets:
            if spreadsheet.name == name:
                return spreadsheet
        return None

    def get_first_sheet_dataframe(self, spreadsheet_name: str) -> pd.DataFrame | None:
        """
        Возвращает DataFrame первого листа указанной книги или None.

        Удобно, когда для каждой программы используется первый лист таблицы.
        """
        spreadsheet = self.get_spreadsheet(spreadsheet_name)
        if spreadsheet is None or not spreadsheet.sheets:
            return None
        return spreadsheet.sheets[0].data


