from pathlib import Path

import gspread
from oauth2client.service_account import ServiceAccountCredentials


def create_gspread_client(service_account_path: Path) -> gspread.Client:
    """
    Создаёт авторизованный gspread.Client по JSON-файлу сервисного аккаунта.

    Пример:
        from pathlib import Path
        from src.bot_core.repository_clients.google_sheets.client import create_gspread_client

        client = create_gspread_client(Path("service_account.json"))
        sheet = client.open("my_spreadsheet").sheet1
    """
    creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_path)
    return gspread.authorize(creds)


